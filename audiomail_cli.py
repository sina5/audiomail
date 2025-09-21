"""
Audio Email Agent using LangGraph for recording, transcription, and email drafting.
"""

from langgraph.graph import StateGraph

from audiomail import AgentState, AudioMail, load_config
from audiomail.utils import get_voice_feedback


def main():
    """Run the audio email agent."""
    # Load configuration and initialize nodes (models, audio settings)
    config = load_config()

    # Initialize nodes instance first
    nodes = AudioMail(config=config)

    # Initialize state
    initial_state = AgentState(
        audio_path="",
        transcription="",
        email_draft="",
        feedback="",
        needs_refinement=False,
        status="starting",
    )

    # Build a state graph workflow
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("record", nodes.record_audio)
    workflow.add_node("transcribe", nodes.transcribe_audio)
    workflow.add_node("draft", nodes.draft_email)
    workflow.add_node("refine", nodes.refine_email)

    # Add edges
    workflow.add_edge("record", "transcribe")
    workflow.add_edge("transcribe", "draft")
    workflow.add_conditional_edges(
        "draft", nodes.should_refine, "refine"
    )  # Only go to refine if needed

    # Set entry point
    workflow.set_entry_point("record")

    # Compile the graph
    app = workflow.compile()

    # Run initial workflow
    state = app.invoke(initial_state)

    # Print initial results
    print("\nTranscription:")
    print(state["transcription"])
    print("\nDrafted Email:")
    print(state["email_draft"])

    # Handle refinements
    while True:
        needs_refinement, feedback = get_voice_feedback(nodes)
        if not needs_refinement:
            break

        print("\nTranscribed Feedback:")
        print(feedback)

        # Update state for refinement
        state["needs_refinement"] = True
        state["feedback"] = feedback

        # Run refinement
        state = nodes.refine_email(state)

        # Show refined email
        print("\nRefined Email:")
        print(state["email_draft"])


if __name__ == "__main__":
    main()
