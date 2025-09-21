"""AudioMail class implementing recording, transcription, and drafting."""

import json
import os
import queue
import re
import tempfile
import threading
import time
from datetime import datetime
from typing import Any

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
import torch
from faster_whisper import WhisperModel
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers import AutoModelForCausalLM, AutoTokenizer

from .state import AgentState
from .utils import (
    get_torch_dtype,
    make_check_stop_flag,
    make_recording_audio_callback,
    make_streamlit_audio_callback,
)


class AudioMail:
    def __init__(self, config: Any, is_streamlit: bool = False):
        """Initialize node helpers, load models and set runtime options.
        Args:
            config: Configuration object with settings
            is_streamlit: Whether running in Streamlit (affects recording behavior)"""

        # Load settings from config
        # Audio settings
        self.sample_rate = config.getint(
            "audio", "sample_rate", fallback=44100
        )
        self.channels = config.getint("audio", "channels", fallback=1)
        self.save_recordings = config.getboolean(
            "audio", "save_recordings", fallback=False
        )

        # Whisper settings
        whisper_model_size = config.get(
            "whisper", "model_size", fallback="tiny"
        )
        whisper_device = config.get("whisper", "device", fallback="cpu")

        # LLM model settings
        model_name = config.get("llm", "model_name", fallback="Qwen/Qwen3-4B")
        model_device = config.get("llm", "device", fallback=None)
        torch_dtype_str = config.get("llm", "dtype", fallback=None)

        # Additional model kwargs from config (optional)
        trust_remote_code_cfg = config.getboolean(
            "llm", "trust_remote_code", fallback=True
        )
        dtype_cfg = config.get("llm", "dtype", fallback="auto")

        # Generation settings
        self.max_new_tokens = config.getint(
            "generation", "max_new_tokens", fallback=512
        )
        self.temperature = config.getfloat(
            "generation", "temperature", fallback=0.7
        )
        self.top_p = config.getfloat("generation", "top_p", fallback=0.95)
        self.do_sample = config.getboolean(
            "generation", "do_sample", fallback=True
        )

        # Path settings
        self.recordings_dir = config.get(
            "audio", "recordings_dir", fallback="recordings"
        )

        # Interface settings
        self.is_streamlit = is_streamlit

        # Auto-detect devices and dtype if not specified
        if whisper_device in [None, "auto"]:
            whisper_device = self.detect_device()
        if model_device in [None, "auto"]:
            model_device = self.detect_device()

        # Choose a dtype appropriate for the target device. Allow config override.
        if dtype_cfg and dtype_cfg not in [None, "auto"]:
            torch_dtype = get_torch_dtype(dtype_cfg)
        elif torch_dtype_str in [None, "auto"]:
            torch_dtype = self.get_optimal_dtype(model_device)
        else:
            torch_dtype = get_torch_dtype(torch_dtype_str)

        # Initialize WhisperModel
        print(f"Initializing Whisper model on {whisper_device}...")
        self.whisper_model_size = whisper_model_size
        self.whisper_model_device = whisper_device
        self.whisper_model = WhisperModel(
            whisper_model_size, device=whisper_device
        )
        # Initialize LLM model and tokenizer with device-specific settings
        print(
            f"Loading LLM model and tokenizer on {model_device} with {torch_dtype}..."
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, trust_remote_code=True
        )

        # Load the LLM model
        self.llm = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=bool(trust_remote_code_cfg),
            dtype=torch_dtype,
            device_map=model_device,
        )

        # Set model to evaluation mode
        self.llm.eval()

        # Enable tokenizer caching
        self.tokenizer.enable_cache = True  # Cache tokenizer outputs

        # Store some generation defaults
        self._input_ids_cache = {}

        # Streamlit-specific state (populated when using web UI)
        self.stream = None
        self.audio_queue = None
        self.stop_event = None
        self.recording_thread = None

    def start_recording_streamlit(self, sample_rate: int, channels: int):
        """Start a non-blocking audio recording stream for Streamlit.
        Args:
            sample_rate (int): Sampling rate for recording
            channels (int): Number of audio channels
        """
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()

        audio_callback = make_streamlit_audio_callback(self.audio_queue)

        self.stream = sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback,
            dtype=np.int16,
        )
        self.stream.start()
        print("Streamlit recording started.")

    def stop_recording_streamlit(
        self, state: AgentState, recordings_dir: str
    ) -> AgentState:
        """Stop the Streamlit recording and save the audio file.
        Args:
            state: The current agent state
            recordings_dir: Directory to save recordings if enabled
        """
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Streamlit recording stopped.")

        recording_buffer = []
        while not self.audio_queue.empty():
            recording_buffer.append(self.audio_queue.get())

        if not recording_buffer:
            state["status"] = "error"
            state["feedback"] = "No audio was recorded."
            return state

        recording = np.concatenate(recording_buffer, axis=0)

        if self.save_recordings:
            # Create permanent recording directory
            os.makedirs(recordings_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.abspath(
                f"{recordings_dir}/audio_{timestamp}.wav"
            )
            wav.write(audio_path, self.sample_rate, recording)
            state["_is_temp_audio"] = False
        else:
            # For Streamlit
            cwd = os.getcwd()
            temp_audio_dir = os.path.join(cwd, "temp_audio")
            os.makedirs(temp_audio_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.abspath(
                os.path.join(temp_audio_dir, f"audio_{timestamp}.wav")
            )

            # Write the wav file
            wav.write(audio_path, self.sample_rate, recording)
            time.sleep(0.5)

            if not os.path.exists(audio_path):
                state["status"] = "error"
                state["feedback"] = (
                    f"Error creating temp audio file at {audio_path}"
                )
                return state

            print(f"Temporary audio saved to: {audio_path}")
            state["_is_temp_audio"] = True

        # Make sure the path is absolute
        state["audio_path"] = os.path.abspath(audio_path)
        state["status"] = "audio_recorded"
        return state

    def record_audio(
        self, state: AgentState, max_duration: int = 300
    ) -> AgentState:
        """Record audio from the user (CLI only).

        Args:
            state: The current agent state
            max_duration: Maximum recording duration in seconds (default: 5 minutes)

        Raises:
            RuntimeError: If no audio device is available or if recording fails
            ValueError: If invalid audio settings are provided
        """
        audio_queue = queue.Queue()
        stop_event = threading.Event()
        start_time = time.time()
        # recording_error is tracked inside recording_error_container created below

        recording_error_container = {"err": None}
        audio_callback = make_recording_audio_callback(
            audio_queue,
            stop_event,
            start_time,
            max_duration,
            recording_error_container,
        )

        check_stop_flag = make_check_stop_flag(stop_event)

        try:
            # Verify audio device availability
            devices = sd.query_devices()
            if not any(device["max_input_channels"] > 0 for device in devices):
                raise RuntimeError(
                    "No input devices found. Please connect a microphone."
                )

            # Start stop checker in a separate thread
            stop_thread = threading.Thread(target=check_stop_flag)
            stop_thread.daemon = True
            stop_thread.start()

            # Start recording with error handling
            try:
                stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    callback=audio_callback,
                    dtype=np.int16,
                )

                with stream:
                    while not stop_event.is_set():
                        time.sleep(0.1)  # Wait for recording to complete

                # Check for any recorded errors
                if recording_error_container.get("err"):
                    raise RuntimeError(recording_error_container["err"])

                # Collect all recorded chunks from the queue (similar to Streamlit approach)
                recording_buffer = []
                while not audio_queue.empty():
                    recording_buffer.append(audio_queue.get())

                if not recording_buffer:
                    raise RuntimeError(
                        "No audio was recorded. Please try again."
                    )

                # Combine all recorded chunks
                recording = np.concatenate(recording_buffer, axis=0)

                # Verify the recording isn't silent
                if np.abs(recording).mean() < 0.01:
                    raise ValueError(
                        "Recording appears to be silent. Please check your microphone."
                    )

                if self.save_recordings:
                    # Create recordings directory if it doesn't exist
                    os.makedirs(self.recordings_dir, exist_ok=True)

                    # Save the recording to disk
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    audio_path = f"{self.recordings_dir}/audio_{timestamp}.wav"
                    wav.write(audio_path, self.sample_rate, recording)

                    print(f"\nRecording saved to {audio_path}")
                else:
                    # Create a temporary file to store the recording
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".wav"
                    ) as tmp_file:
                        wav.write(tmp_file.name, self.sample_rate, recording)
                        audio_path = tmp_file.name
                    print("\nRecording finished, using temporary file.")

                state["audio_path"] = audio_path
                state["status"] = "audio_recorded"
                return state

            except (sd.PortAudioError, OSError) as e:
                raise RuntimeError(f"Error during recording: {str(e)}")

        except Exception as e:
            print(f"\nError: {str(e)}")
            state["status"] = "error"
            state["feedback"] = str(e)
            return state

    def transcribe_audio(self, state: AgentState) -> AgentState:
        """Transcribe the recorded audio using FastWhisper."""
        audio_path = state["audio_path"]

        # Verify file exists and is accessible
        if not os.path.exists(audio_path):
            state["status"] = "error"
            state["feedback"] = f"Audio file not found: {audio_path}"
            return state

        try:
            # Add extra debug info
            print(f"File exists: {os.path.exists(audio_path)}")
            print(f"File size: {os.path.getsize(audio_path)} bytes")
            print(f"File permissions: {oct(os.stat(audio_path).st_mode)[-3:]}")

            # Use absolute path
            abs_path = os.path.abspath(audio_path)
            print(f"Using absolute path for transcription: {abs_path}")

            # Transcribe using the absolute path
            segments, _ = self.whisper_model.transcribe(abs_path)

            # Combine all segments into one transcription
            transcription = " ".join([segment.text for segment in segments])

            print("Transcription:", transcription)

            state["transcription"] = transcription
            state["status"] = "transcribed"

        except Exception as e:
            import traceback

            traceback_str = traceback.format_exc()
            state["status"] = "error"
            state["feedback"] = (
                f"Transcription error: {str(e)}\n{traceback_str}"
            )
            print(f"Transcription error: {str(e)}")
            print(f"Traceback: {traceback_str}")
            return state

        # Only delete temporary files if not running in Streamlit
        # Streamlit may need access to the file later
        if (
            not self.is_streamlit
            and state.get("_is_temp_audio")
            and os.path.exists(audio_path)
        ):
            try:
                os.remove(audio_path)
                print(f"Removed temporary audio file: {audio_path}")
            except Exception as e:
                print(f"Warning: Could not delete temp audio file: {e}")

        return state

    def draft_email(self, state: AgentState) -> AgentState:
        """Draft a professional email using local Qwen model."""
        prompt = (
            "You are an expert email assistant. Based on the following "
            "transcription, draft a professional email. The email should "
            "have a clear subject, a proper salutation, and a body that "
            "reflects the transcription's content.\n\n"
            f'Transcription: "{state["transcription"]}"\n\n'
            "Return the complete email as a JSON object with a single "
            "key: 'email_draft'. The value should be a single string "
            "containing the entire email, with newlines for formatting."
        )

        # Prepare the input and check cache
        messages = [{"role": "user", "content": prompt}]
        input_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False
        )

        # Check if we have cached inputs for this text
        if input_text in self._input_ids_cache:
            model_inputs = self._input_ids_cache[input_text]
        else:
            model_inputs = self.tokenizer(
                [input_text], return_tensors="pt", padding=True
            ).to(self.llm.device)
            self._input_ids_cache[input_text] = model_inputs

        print("Generating email draft...\n")
        # Generate response with optimized settings
        with torch.inference_mode():  # Faster than no_grad
            with sdpa_kernel(SDPBackend.FLASH_ATTENTION):
                generated_ids = self.llm.generate(
                    **model_inputs,
                    max_new_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    do_sample=self.do_sample,
                    use_cache=True,  # Enable KV cache
                    num_beams=1,  # Disable beam search for speed
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

        # Decode the response
        response_text = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]

        # Find the last JSON block in the response
        json_matches = re.findall(r"\{.*?\}", response_text, re.DOTALL)

        email_draft = ""
        if json_matches:
            # Try to parse the last found JSON block
            last_json_part = json_matches[-1]
            try:
                email_data = json.loads(last_json_part)
                email_draft = email_data.get("email_draft", "").strip()
            except json.JSONDecodeError:
                # Fallback if JSON is invalid
                email_draft = response_text.strip()
        else:
            # Fallback if no JSON is found
            email_draft = response_text.strip()

        state["email_draft"] = email_draft
        state["status"] = "completed"
        state["needs_refinement"] = False  # Reset refinement flag
        return state

    def refine_email(self, state: AgentState) -> AgentState:
        """Refine the email draft based on user feedback."""
        prompt = (
            "Please refine the following email draft based on the user's feedback:\n"
            f"Original Draft:\n{state['email_draft']}\n\n"
            f"User Feedback:\n{state['feedback']}\n\n"
            "Please provide an improved version of the email that addresses "
            "the feedback while maintaining professional email etiquette"
        )

        # Prepare the input and check cache
        messages = [{"role": "user", "content": prompt}]
        input_text = self.tokenizer.apply_chat_template(
            messages, tokenize=False
        )

        # Check if we have cached inputs for this text
        if input_text in self._input_ids_cache:
            model_inputs = self._input_ids_cache[input_text]
        else:
            model_inputs = self.tokenizer(
                [input_text], return_tensors="pt", padding=True
            ).to(self.llm.device)
            self._input_ids_cache[input_text] = model_inputs

        # Generate response with optimized settings
        with torch.inference_mode():  # Faster than no_grad
            generated_ids = self.llm.generate(
                **model_inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                do_sample=self.do_sample,
                use_cache=True,  # Enable KV cache
                num_beams=1,  # Disable beam search for speed
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode the response
        refined_draft = self.tokenizer.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        refined_draft = refined_draft[len(input_text) :].strip()

        state["email_draft"] = refined_draft
        state["status"] = "refined"
        state["needs_refinement"] = False
        return state

    @staticmethod
    def should_refine(state: AgentState) -> bool:
        """Determine if the email needs refinement."""
        return state["needs_refinement"]

    @staticmethod
    def detect_device():
        """Detect the best available device for model inference."""
        if torch.backends.mps.is_available():
            return "mps"  # Metal Performance Shaders for Apple Silicon
        elif torch.cuda.is_available():
            return "cuda"
        return "cpu"

    @staticmethod
    def get_optimal_dtype(device: str) -> torch.dtype:
        """Get the optimal dtype for the given device."""
        if device == "mps":
            # MPS works best with float32 for now
            return torch.float32
        else:
            # Use float16 for CUDA and CPU for efficiency
            return torch.float16
