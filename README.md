# 🔎 Multi-Agent Research System

A **LangGraph-powered multi-agent research system** that autonomously researches a user query, gathers web evidence, analyzes the collected information, critically evaluates the research, and produces a synthesized final answer.

The system uses a **Supervisor → Researcher → Analyst → Critic → Synthesis** architecture with conditional routing, tool calling, research feedback loops, execution limits, persistent checkpointing, and a Streamlit interface for interactive research.

---

## ✨ Overview

Traditional LLM applications generally follow a simple pattern:

```text
User Query
    ↓
LLM
    ↓
Answer
```

This project explores a more structured **agentic workflow**:

```text
                         ┌──────────────┐
                         │  Supervisor  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Researcher  │
                         └──────┬───────┘
                                │
                         Web Search / Fetch
                                │
                                ▼
                         ┌──────────────┐
                         │   Analyst    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Critic    │
                         └──────┬───────┘
                                │
                     ┌──────────┴──────────┐
                     │                     │
                 Research Required       Pass
                     │                     │
                     ▼                     ▼
                Researcher            Supervisor
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   Synthesis  │
                                    └──────┬───────┘
                                           │
                                           ▼
                                      Final Answer
```

Instead of relying on a single model call, different agents have clearly defined responsibilities.

---

# 🚀 Features

* 🧠 **Supervisor Agent** for workflow coordination and routing
* 🌐 **Researcher Agent** with web search and webpage fetching tools
* 📊 **Analyst Agent** for organizing and interpreting evidence
* 🔍 **Critic Agent** for evaluating research quality and identifying gaps
* ✍️ **Synthesis Agent** for producing the final response
* 🔄 **Critic-driven research loop**
* 🛠️ **LLM tool calling**
* 🌐 Web search using DuckDuckGo
* 📄 Webpage content extraction
* 🔗 Source collection and deduplication
* 📈 Research metrics
* 🔢 Tool-call tracking
* 🔄 Research-round tracking
* 🛑 Maximum iteration limits
* 🛑 Maximum research-round limits
* 🛑 Maximum tool-call limits
* 🛡️ Error handling and graceful fallbacks
* 💾 Persistent LangGraph checkpointing with SQLite
* 🧵 Unique thread IDs for executions
* 🖥️ Interactive Streamlit interface
* 📋 Live agent workflow visualization
* 📚 Expandable research sources
* 📊 Analyst and Critic inspection
* 💬 Chat-style research input

---

# 🏗️ System Architecture

The system is divided into two major layers:

```text
┌─────────────────────────────────────────────────────┐
│                  Streamlit Interface                │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                    Main Graph                       │
│                                                     │
│  Supervisor → Researcher → Analyst → Critic         │
│                              ↑       │              │
│                              │       │              │
│                              └───────┘              │
│                                      │              │
│                                 Supervisor          │
│                                      │              │
│                                      ▼              │
│                                  Synthesis          │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
                Final Research Answer
```

---

# 🤖 Agents

## 1. Supervisor

The Supervisor is responsible for coordinating the overall workflow.

It determines which stage should execute next based on the current state.

Possible routing decisions include:

```text
research
analyst
critic
synthesis
```

The Supervisor also considers:

* Whether research exists
* Whether analysis exists
* Whether critique has passed
* Whether research is complete
* Current iteration
* Research-round limits

### Responsibility

> Coordinate the workflow rather than perform the research itself.

---

## 2. Researcher

The Researcher is responsible for gathering external information.

It has access to two tools:

### Web Search

Searches the web for relevant information.

```text
User Query
    ↓
Researcher
    ↓
Web Search
    ↓
Search Results
```

### Web Fetch

Fetches and extracts readable content from useful webpages.

```text
Search Result
    ↓
URL
    ↓
Web Fetch
    ↓
Extracted Page Content
```

The Researcher can decide when additional searches or webpage fetching are necessary.

---

## 3. Analyst

The Analyst processes the collected research.

Its role is to:

* Organize evidence
* Identify important information
* Compare findings
* Detect patterns
* Identify conflicting information
* Interpret the collected evidence
* Prepare structured information for the Critic

The Analyst does **not** perform web research itself.

---

## 4. Critic

The Critic acts as a validation layer.

It evaluates whether the collected research and analysis are sufficient to answer the original query.

It checks for:

* Missing information
* Weak evidence
* Unsupported conclusions
* Contradictions
* Insufficient research
* Evidence gaps

The Critic produces one of two workflow outcomes:

```text
PASS
  ↓
Synthesis

RESEARCH REQUIRED
  ↓
Researcher
```

This creates a feedback loop rather than forcing the system to generate an answer immediately.

---

## 5. Synthesis

The Synthesis Agent produces the final answer.

It receives:

* Original query
* Research results
* Sources
* Analyst findings
* Critic evaluation

It then generates a coherent final response based on the available evidence.

---

# 🔄 Workflow

A typical successful execution follows:

```text
START
  │
  ▼
Supervisor
  │
  ▼
Researcher
  │
  ├── Web Search
  │
  ├── Web Fetch
  │
  ▼
Analyst
  │
  ▼
Critic
  │
  ├── Research Required ──────┐
  │                           │
  │                           ▼
  │                       Researcher
  │
  └── PASS
        │
        ▼
    Supervisor
        │
        ▼
    Synthesis
        │
        ▼
       END
```

The Critic can therefore send the workflow back to the Researcher when additional research is needed.

---

# 🧠 Why a Multi-Agent Architecture?

A single LLM can potentially perform all of these tasks, but separating responsibilities provides a more structured architecture.

Instead of:

```text
LLM
 ↓
Do Everything
```

the system separates:

```text
Planning
   ↓
Research
   ↓
Analysis
   ↓
Validation
   ↓
Synthesis
```

This makes it easier to:

* Debug individual stages
* Control tool usage
* Inspect intermediate reasoning outputs
* Add specialized agents
* Implement feedback loops
* Track execution
* Apply execution limits
* Evaluate individual components

---

# 🛠️ Technology Stack

| Technology        | Purpose                                    |
| ----------------- | ------------------------------------------ |
| Python            | Core programming language                  |
| LangGraph         | Agent orchestration and stateful workflows |
| LangChain         | LLM and tool integration                   |
| Google Gemini     | LLM powering the agents                    |
| DuckDuckGo Search | Web search                                 |
| Requests          | Webpage fetching                           |
| BeautifulSoup     | HTML parsing and text extraction           |
| SQLite            | Persistent checkpoint storage              |
| Streamlit         | Interactive user interface                 |
| python-dotenv     | Environment configuration                  |

---

# 📁 Project Structure

```text
multi-agent-research-system/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── research_system.db
├── README.md
│
├── tests/
│   └── test_graph.py
│
└── src/
    │
    ├── config.py
    │
    ├── state/
    │   ├── state.py
    │   └── defaults.py
    │
    ├── nodes/
    │   ├── supervisor.py
    │   ├── researcher.py
    │   ├── research_extractor.py
    │   ├── analyst.py
    │   ├── critic.py
    │   └── synthesis.py
    │
    ├── graph/
    │   ├── graph.py
    │   ├── routing.py
    │   ├── research_graph.py
    │   ├── research_routing.py
    │   └── checkpointer.py
    │
    ├── tools/
    │   ├── search.py
    │   └── fetch.py
    │
    └── utils/
        └── content.py
```

> File names may vary slightly depending on the current implementation, but the project is organized around **state, nodes, graphs, routing, tools, and prompts**.

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/your-username/multi-agent-research-system.git
cd multi-agent-research-system
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If Streamlit is not already included:

```bash
pip install streamlit
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

The project loads the API key through `python-dotenv`.

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
research_system.db
```

Never commit your API key to GitHub.

---

# ▶️ Running the Application

## Streamlit Interface

Run:

```bash
streamlit run app.py
```

The application provides a chat-style interface where you can enter a research question.

For example:

```text
What are the main differences between LangGraph and CrewAI?
```

The submitted question appears in the interface, followed by the live multi-agent workflow.

---

## CLI Interface

The project also provides a command-line interface:

```bash
python main.py
```

You can then enter a research question directly in the terminal.

---

# 🖥️ Streamlit Interface

The Streamlit interface provides several sections.

## Query

The user enters a research question through the chat-style input.

```text
Enter your research question...
```

---

## Agent Workflow

The interface visually tracks the five agents:

```text
🧠 Supervisor
🌐 Researcher
📊 Analyst
🔍 Critic
✍️ Synthesis
```

Each agent can appear as:

```text
🟢 Running
✅ Completed
⚪ Waiting
```

---

## Execution

The execution panel displays:

* Current agent
* Progress
* Event history
* Iteration information

---

## Final Answer

After the workflow completes, the generated answer is displayed.

---

## Research Metrics

The application tracks:

```text
Iterations
Research Rounds
Tool Calls
Sources
```

These metrics provide visibility into how the agent system executed.

---

## Research Sources

Collected research results can be expanded individually to inspect:

* Source title
* URL
* Extracted webpage content

---

## Analyst Analysis

The Analyst's intermediate output can be inspected through the expandable analysis section.

---

## Critic Evaluation

The Critic's evaluation is also available.

The interface indicates:

```text
Critic decision: PASS
```

or:

```text
Critic decision: RESEARCH REQUIRED
```

---

# 🧩 LangGraph State

The agents communicate through a shared `AgentState`.

A simplified representation is:

```python
class AgentState(TypedDict):
    query: str

    messages: list

    current_agent: str
    next_agent: str

    research_results: list
    sources: list

    research_complete: bool

    analysis: str

    critique: str
    critique_passed: bool

    final_answer: str

    iteration: int
    research_round: int
    tool_calls: int
```

This shared state allows each node to consume information produced by previous nodes.

---

# 🛡️ Production Hardening

The project includes several mechanisms designed to prevent uncontrolled agent execution.

## Maximum Iterations

The entire workflow has a maximum iteration limit.

```python
MAX_ITERATIONS = 15
```

---

## Maximum Research Rounds

The Critic cannot continuously send the workflow back to the Researcher.

```python
MAX_RESEARCH_ROUNDS = 3
```

---

## Maximum Tool Calls

The Researcher is also restricted by a maximum number of tool calls.

```python
MAX_TOOL_CALLS = 12
```

These limits help control:

* API usage
* Execution time
* Infinite loops
* Unexpected agent behavior

---

# 🛑 Error Handling

Agent nodes and external tools contain error handling so failures can be handled gracefully.

For example, web search failures return a tool-level error rather than crashing the entire workflow.

The system also includes fallback behavior for:

* Researcher failures
* Analyst failures
* Critic failures
* Synthesis failures
* Web search failures
* Web fetch failures

---

# 💾 Persistent Checkpointing

The project uses LangGraph checkpointing with SQLite.

A SQLite database is used to persist graph execution state.

```text
research_system.db
```

This enables executions to be associated with unique thread IDs.

Each execution receives a unique identifier:

```python
thread_id = str(uuid.uuid4())
```

The graph receives the thread ID through LangGraph configuration:

```python
config = {
    "configurable": {
        "thread_id": thread_id
    }
}
```

This provides a foundation for persistent and resumable workflows.

---

# 🔧 Tools

## Web Search

The Researcher uses DuckDuckGo search to retrieve web results.

The search tool returns information such as:

```text
Title
URL
Snippet
```

---

## Web Fetch

The Web Fetch tool retrieves webpage content using HTTP requests and extracts readable text using BeautifulSoup.

Unnecessary HTML elements such as:

```text
script
style
nav
footer
header
aside
```

are removed before extracting the page text.

The extracted content is also limited to prevent excessively large inputs to the LLM.

---

# 🔄 Research Feedback Loop

One of the key features of the project is the Critic → Researcher feedback loop.

For example:

```text
Research
   ↓
Analysis
   ↓
Critic
   ↓
Insufficient Evidence
   ↓
Research
```

The Researcher can then gather additional information before the system attempts synthesis again.

This makes the workflow more adaptive than a fixed sequential pipeline.

---

# 📊 Example Workflow

For a question such as:

```text
Who is Tesla's current CEO?
```

the workflow can look like:

```text
User Query
    ↓
Supervisor
    ↓
Researcher
    ↓
Web Search
    ↓
Web Fetch
    ↓
Research Results
    ↓
Analyst
    ↓
Evidence Analysis
    ↓
Critic
    ↓
Evidence Sufficient
    ↓
Supervisor
    ↓
Synthesis
    ↓
Final Answer
```

---

# 🎯 Design Goals

This project was designed to explore several important concepts in modern agentic AI systems:

### Agent orchestration

Using LangGraph to coordinate multiple specialized agents.

### Stateful workflows

Maintaining shared state across multiple graph nodes.

### Tool-using agents

Allowing an LLM to decide when external tools are required.

### Conditional routing

Allowing workflow decisions to depend on the current state.

### Feedback loops

Allowing the Critic to request additional research.

### Execution control

Using iteration, research-round, and tool-call limits.

### Observability

Tracking intermediate agent activity and execution metrics.

### Persistence

Using checkpointing and thread IDs for stateful executions.

---

# 🔮 Future Improvements

Potential future extensions include:

* 🔬 Automated research-quality evaluation
* 📊 Benchmarking answer quality
* 🎯 Source relevance scoring
* 🧪 Critic accuracy evaluation
* 🧭 Routing accuracy evaluation
* ⏱️ Latency tracking
* 📉 Failure-rate monitoring
* 🧠 More specialized research agents
* 🔗 Source credibility scoring
* 📝 Citation-aware final answers
* 🗄️ Persistent research history
* 🔐 Authentication
* 🌐 Deployment to a cloud platform
* 📡 Streaming token-level responses
* 🧪 Automated evaluation datasets
* 📈 LangSmith-based observability and evaluation

---

# 🧪 Evaluation Roadmap

A future evaluation phase can measure:

| Metric               | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| Research Quality     | How useful and complete the collected research is            |
| Source Relevance     | How relevant retrieved sources are to the query              |
| Critic Accuracy      | Whether the Critic correctly identifies research gaps        |
| Routing Accuracy     | Whether the Supervisor chooses the appropriate next agent    |
| Tool Efficiency      | Number of unnecessary tool calls                             |
| Iteration Count      | Number of workflow iterations                                |
| Latency              | Total execution time                                         |
| Failure Rate         | Frequency of failed executions                               |
| Final Answer Quality | Accuracy, completeness, and usefulness of the final response |

---

# ⚠️ Limitations

This project is an experimental agentic research system and should not be treated as a guaranteed source of truth.

Potential limitations include:

* Search results can contain inaccurate or outdated information.
* Webpages may block automated requests.
* Some webpages may not expose their content through standard HTTP requests.
* LLM-generated analysis can contain errors.
* The Critic does not guarantee factual correctness.
* Search coverage depends on the underlying search engine.
* Gemini API availability and quotas can affect execution.
* The system does not currently provide formal citation verification.

For high-stakes decisions, information should be independently verified against authoritative sources.

---

# 🔐 Security Considerations

Do not commit:

```text
.env
API keys
credentials
private configuration
research_system.db
```

Recommended `.gitignore`:

```gitignore
.env
venv/
.venv/
__pycache__/
*.pyc
research_system.db
.streamlit/
```

---

# 📚 Key Concepts Demonstrated

This project demonstrates practical implementation of:

* Agentic AI
* Multi-agent systems
* LangGraph
* LangChain
* State graphs
* Conditional routing
* Supervisor agents
* Tool calling
* Web research agents
* Agent feedback loops
* Structured state management
* Execution limits
* Error handling
* Checkpointing
* Thread-based execution
* Streamlit
* LLM orchestration

---

# 👨‍💻 Project Purpose

This project was built as a hands-on exploration of **Agentic AI and multi-agent orchestration**.

The primary objective was to move beyond simple LLM applications and implement a system where multiple specialized agents collaborate through a structured stateful workflow.

The project focuses particularly on:

```text
LLM
 ↓
Tools
 ↓
Agents
 ↓
State
 ↓
Routing
 ↓
Feedback
 ↓
Evaluation
```

rather than treating an LLM as a single isolated chatbot.

---

# 📄 License

This project is available under the MIT License.

See the `LICENSE` file for details.

---

# ⭐ Acknowledgments

Built using:

* LangGraph
* LangChain
* Google Gemini
* DuckDuckGo Search
* BeautifulSoup
* Streamlit

---

## 🚀 Getting Started

```bash
git clone https://github.com/your-username/multi-agent-research-system.git

cd multi-agent-research-system

python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure API key
# Create .env and add GOOGLE_API_KEY

# Run
streamlit run app.py
```

Then enter a research question and let the multi-agent workflow research, analyze, critique, and synthesize the answer.

```

