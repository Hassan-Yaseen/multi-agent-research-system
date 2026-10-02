import os

from dotenv import load_dotenv


load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set.")

# ============================================================
# Execution limits
# ============================================================

MAX_ITERATIONS = 15

MAX_RESEARCH_ROUNDS = 3

MAX_TOOL_CALLS = 12