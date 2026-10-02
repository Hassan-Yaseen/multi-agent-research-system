from src.graph.graph import build_graph


def test_graph():

    graph = build_graph()

    initial_state = {
        "query": "What is LangGraph?",

        "messages": [],

        "current_agent": "",

        "next_agent": "",

        "research_results": [],

        "sources": [],

        "iteration": 0,

        "final_answer": "",
    }

    result = graph.invoke(initial_state)

    assert result["query"] == "What is LangGraph?"

    assert result["iteration"] >= 0