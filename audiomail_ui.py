"""Streamlit UI for AudioMail: simple controls to record, transcribe and refine emails."""

import streamlit as st

from audiomail import AgentState, AudioMail, load_config

# UI title
st.title("Audiomail Agent")

# Initialize agent and state
if "agent" not in st.session_state:
    config = load_config()
    st.session_state.agent = AudioMail(config=config, is_streamlit=True)
if "state" not in st.session_state:
    st.session_state.state = AgentState(
        audio_path="",
        transcription="",
        email_draft="",
        feedback="",
        needs_refinement=False,
        status="idle",
    )
if "recording" not in st.session_state:
    st.session_state.recording = False
if "feedback_recording" not in st.session_state:
    st.session_state.feedback_recording = False

# --- Main Recording Section ---
st.header("1. Record Your Instructions")
col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Start Recording",
        disabled=st.session_state.recording
        or st.session_state.feedback_recording,
    ):
        st.session_state.recording = True
        st.session_state.agent.start_recording_streamlit(
            sample_rate=st.session_state.agent.sample_rate,
            channels=st.session_state.agent.channels,
        )
        st.rerun()

with col2:
    if st.button("Stop Recording", disabled=not st.session_state.recording):
        st.session_state.recording = False
        with st.spinner("Processing audio..."):
            # Stop recording and save audio
            state = st.session_state.agent.stop_recording_streamlit(
                st.session_state.state,
                recordings_dir=st.session_state.agent.recordings_dir,
            )
            st.session_state.state = state

            # Transcribe, then draft
            if state.get("audio_path"):
                with st.spinner("Transcribing..."):
                    st.session_state.state = (
                        st.session_state.agent.transcribe_audio(
                            st.session_state.state
                        )
                    )
                with st.spinner("Drafting email..."):
                    st.session_state.state = (
                        st.session_state.agent.draft_email(
                            st.session_state.state
                        )
                    )
        st.rerun()

if st.session_state.recording:
    st.info("Recording instructions in progress...")

# --- Display Results and Refinement ---
if st.session_state.state and st.session_state.state.get("status") != "idle":
    if st.session_state.state.get("audio_path"):
        st.subheader("Original Recording")
        st.audio(st.session_state.state["audio_path"])

    if st.session_state.state.get("transcription"):
        st.subheader("Transcription")
        st.write(st.session_state.state["transcription"])

    if st.session_state.state.get("email_draft"):
        st.header("2. Review and Refine Email")
        st.text_area(
            "Email Draft", st.session_state.state["email_draft"], height=300
        )

        st.subheader("3. Refine with Voice Feedback")

        # --- Feedback Recording Section ---
        col3, col4 = st.columns(2)
        with col3:
            if st.button(
                "Start Feedback Recording",
                disabled=st.session_state.recording
                or st.session_state.feedback_recording,
            ):
                st.session_state.feedback_recording = True
                # Use a different state for feedback to not overwrite the main audio
                st.session_state.feedback_state = AgentState(
                    audio_path="",
                    transcription="",
                    email_draft="",
                    feedback="",
                    needs_refinement=False,
                    status="feedback",
                )
                st.session_state.agent.start_recording_streamlit(
                    sample_rate=st.session_state.agent.sample_rate,
                    channels=st.session_state.agent.channels,
                )
                st.rerun()

        with col4:
            if st.button(
                "Stop Feedback Recording",
                disabled=not st.session_state.feedback_recording,
            ):
                st.session_state.feedback_recording = False
                with st.spinner("Processing feedback..."):
                    # Stop feedback recording
                    feedback_state = st.session_state.agent.stop_recording_streamlit(
                        st.session_state.feedback_state,
                        recordings_dir=st.session_state.agent.recordings_dir,
                    )

                    # Transcribe feedback
                    if feedback_state.get("audio_path"):
                        with st.spinner("Transcribing feedback..."):
                            feedback_state = (
                                st.session_state.agent.transcribe_audio(
                                    feedback_state
                                )
                            )

                        # Update main state with feedback and refine
                        main_state = st.session_state.state
                        main_state["feedback"] = feedback_state[
                            "transcription"
                        ]
                        main_state["needs_refinement"] = True

                        with st.spinner("Refining email..."):
                            st.session_state.state = (
                                st.session_state.agent.refine_email(main_state)
                            )
                st.rerun()

        if st.session_state.feedback_recording:
            st.info("Recording feedback in progress...")

# --- Clear Button ---
if st.button("Clear and Start Over"):
    st.session_state.state = AgentState(
        audio_path="",
        transcription="",
        email_draft="",
        feedback="",
        needs_refinement=False,
        status="idle",
    )
    st.session_state.recording = False
    st.session_state.feedback_recording = False
    st.rerun()
