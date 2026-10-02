import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


def create_checkpointer():

    connection = sqlite3.connect(
        "research_system.db",
        check_same_thread=False,
    )

    return SqliteSaver(connection)