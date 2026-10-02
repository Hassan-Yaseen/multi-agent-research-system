import uuid

from src.graph.graph import build_graph
from src.state.defaults import create_initial_state


def main():

    print("\n=== Multi-Agent Research System ===\n")

    query = input(
        "Enter your research question: "
    ).strip()

    if not query:
        print("No query provided.")
        return

    graph = build_graph()

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = create_initial_state(query)

    final_state = None

    for event in graph.stream(
        initial_state,
        config=config,
        stream_mode="values",
    ):

        final_state = event

        print(
            f"\n→ {event.get('current_agent', 'unknown')}"
        )

        print(
            f"Iteration: {event.get('iteration', 0)}"
        )

        print(
            f"Research round: "
            f"{event.get('research_round', 0)}"
        )

        print(
            f"Tool calls: "
            f"{event.get('tool_calls', 0)}"
        )

    if final_state:

        print("\n" + "=" * 70)
        print("FINAL ANSWER")
        print("=" * 70)

        print(
            final_state.get(
                "final_answer",
                "No final answer generated."
            )
        )

if __name__ == "__main__":
    main()