from typing import TypedDict


class AgentState(TypedDict):
    audio_path: str
    transcription: str
    email_draft: str
    status: str
    feedback: str
    needs_refinement: bool
