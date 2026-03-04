# DataSense AI

![CI](https://github.com/saga0302/datasense-ai/actions/workflows/ci.yml/badge.svg)

**Autonomous Pipeline Monitoring & Incident Response Agent**

> An AI-powered data reliability platform that autonomously detects pipeline failures, classifies root causes, maps downstream impact, and generates executive-grade incident reports all without human intervention.

**[Live Demo](https://datasense-ai-mkpy6qfcyxvamtvnvhyzxv.streamlit.app)**

---

## What It Does

1. **Detects** — Claude autonomously requests failed pipeline data through MCP tools
2. **Classifies** — Claude AI classifies failure type using RAG prompt engineering, retrieving similar past incidents from ChromaDB vector store to improve accuracy
3. **Investigates** — Claude requests full dependency map through MCP, tracing upstream sources and downstream blast radius across 9+ systems
4. **Reports** — Generates a professional Root Cause Analysis report automatically
5. **Notifies** — Saves report and sends alerts to the team

---

## Architecture
```
Pipeline Failure Detected
         ↓
[Node 1] detect_anomaly      → Requests failed pipelines via MCP tool
         ↓
[Node 2] classify_failure    → Claude AI classifies failure type
                               + RAG retrieves similar past incidents
                                 from ChromaDB vector store
         ↓
[Node 3] investigate_upstream → Requests dependency map via MCP tool
                                 Maps upstream sources + downstream
                                 blast radius across 9+ systems
         ↓
[Node 4] generate_rca        → Claude AI writes executive RCA report
         ↓
[Node 5] notify_and_save     → Saves .md + .json report, triggers alert
         ↓
      [END] Incident resolved in under 60 seconds
```

**Data Layer:** `data/mock_data.py` — single source of truth for all pipeline and dependency data

**MCP Layer:** `mcp_server.py` exposes `scan_pipelines` and `get_downstream_impact` as MCP endpoints

**RAG Layer:** `nodes/rag_retriever.py` indexes past incidents into ChromaDB and retrieves similar historical context on every classification
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent Orchestration | LangGraph (StateGraph) |
| Generative AI | Anthropic Claude API |
| Agent Tool Protocol | Model Context Protocol (MCP) |
| Vector Store / RAG | ChromaDB + LangChain |
| Dashboard | Streamlit |
| CI/CD | GitHub Actions + pytest |

---

## Key Results

- Monitors **5 simulated pipelines** modeled after real Azure Data Factory infrastructure
- Detects failures and maps **9 downstream systems** at risk
- Generates complete RCA report in **under 60 seconds**
- RAG pipeline retrieves **historical incident context** from ChromaDB vector store
- MCP server exposes **pipeline diagnostic tools** as Model Context Protocol endpoints
- **6 automated tests** passing via GitHub Actions CI/CD
- Deployed live on Streamlit Cloud

---

## Running Locally
```bash
# Clone the repo
git clone https://github.com/saga0302/datasense-ai.git
cd datasense-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Run the dashboard
python -m streamlit run dashboard.py
```

---

## Running Tests
```bash
python -m pytest tests/ -v
```

---

## Real-World Context

Data pipeline failures are one of the most common and costly problems in data engineering. When a pipeline breaks, an on call engineer manually digs through logs, traces dependencies, identifies the root cause, and writes an incident report, a process that can take hours while downstream dashboards, reports, and models sit broken.

DataSense AI automates this entire workflow. A LangGraph agent autonomously requests live pipeline data and dependency maps through Model Context Protocol (MCP) tools, uses Claude AI to classify root causes and investigate blast radius across 9+ downstream systems, and delivers a professional incident report in seconds with no human intervention required.

Same problem every data team faces. Solved with AI.

---

*Built by Sagarika Raju — MS Analytics, University of Southern California*
