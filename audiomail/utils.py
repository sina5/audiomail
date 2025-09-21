import configparser
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

import torch

from .state import AgentState

# Platform-specific imports handled lazily where used
if os.name == "nt":
    import msvcrt
else:
    import termios
    import tty


def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """Load configuration from file. Raises if missing so caller can handle it."""
    config = configparser.ConfigParser()
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    config.read(config_path)
    return config


def get_torch_dtype(dtype_str: str) -> torch.dtype:
    """Convert string dtype to torch.dtype with sensible default."""
    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }
    return dtype_map.get(dtype_str.lower(), torch.float16)


def is_s_pressed():
    """Check if the 's' key is pressed (cross-platform helper)."""
    if os.name == "nt":  # Windows
        return msvcrt.kbhit() and msvcrt.getch().decode().lower() == "s"
    else:  # Unix-like
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch.lower() == "s"


def get_voice_feedback(nodes: Any) -> tuple[bool, str]:
    """Get voice feedback from the user about the email draft."""
    while True:
        response = (
            input("\nWould you like to refine the email? (y/n): ")
            .lower()
            .strip()
        )
        if response.lower() in ["yes", "y"]:
            print(
                "\nPlease provide your voice feedback for improving the email..."
            )
            # Create a temporary state for feedback recording/transcription
            feedback_state = AgentState(
                audio_path="",
                transcription="",
                email_draft="",
                feedback="",
                needs_refinement=False,
                status="feedback",
            )

            # Record and transcribe feedback using the same nodes instance
            feedback_state = nodes.record_audio(feedback_state)
            feedback_state = nodes.transcribe_audio(feedback_state)

            return True, feedback_state["transcription"]
        elif response.lower() in ["no", "n"]:
            return False, ""
        else:
            print("Please answer 'yes'/'y' or 'no'/'n'")


def make_streamlit_audio_callback(audio_queue) -> Callable:
    """Return a sounddevice-compatible callback that pushes audio frames to a queue.

    Args:
        audio_queue: queue.Queue to put audio chunks into
    """

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Audio stream error: {status}")
            return
        audio_queue.put(indata.copy())

    return audio_callback


def make_recording_audio_callback(
    audio_queue,
    stop_event,
    start_time: float,
    max_duration: int,
    recording_error_container: dict,
) -> Callable:
    """Factory for the CLI recording callback used in `record_audio`.

    The callback writes to `audio_queue`. On errors it records the error
    string into `recording_error_container['err']` and sets `stop_event`.
    """

    def audio_callback(indata, frames, time_info, status):
        if status:
            recording_error_container["err"] = f"Audio stream error: {status}"
            stop_event.set()
            return

        if not stop_event.is_set():
            if time.time() - start_time > max_duration:
                print(
                    f"\nMaximum recording duration ({max_duration}s) reached."
                )
                stop_event.set()
                return
            audio_queue.put(indata.copy())

    return audio_callback


def make_check_stop_flag(stop_event) -> Callable:
    """Return a function that checks for the 's' key to stop recording.

    Meant to be run in a separate thread: target=make_check_stop_flag(stop_event)
    """

    def check_stop_flag():
        print("\nRecording... Press 's' to stop")
        print("Speak your message now...")

        while not stop_event.is_set():
            if is_s_pressed():
                print("\nStopping recording...")
                stop_event.set()
                break
            time.sleep(0.1)

    return check_stop_flag
