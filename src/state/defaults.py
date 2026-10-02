def create_initial_state(query: str) -> dict:
    return {
        "query": query,
        "messages": [],
        "current_agent": "",
        "next_agent": "",

        "research_results": [],
        "sources": [],
        "research_complete": False,

        "analysis": "",
        "critique": "",
        "critique_passed": False,

        "final_answer": "",

        "iteration": 0,
        "research_round": 0,
        "tool_calls": 0,
    }