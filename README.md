# DataSense AI

![CI](https://github.com/saga0302/datasense-ai/actions/workflows/ci.yml/badge.svg)

**Autonomous Pipeline Monitoring & Incident Response Agent**

> An AI-powered data reliability platform that autonomously detects pipeline failures, classifies root causes, maps downstream impact, and generates executive-grade incident reports all without human intervention.

**[Live Demo](https://datasense-ai-mkpy6qfcyxvamtvnvhyzxv.streamlit.app)**

---

## What It Does

When a data pipeline fails, DataSense AI:

1. **Detects** — Scans all pipelines and identifies failures instantly
2. **Classifies** — Uses Claude AI to classify failure type (timeout, schema error, permissions, etc.)
3. **Investigates** — Maps the full blast radius across upstream and downstream dependencies
4. **Reports** — Generates a professional Root Cause Analysis report automatically
5. **Notifies** — Saves the report and sends alerts to the team

**Result:** Mean time to resolution drops from hours to seconds.

---

## Architecture
```
Pipeline Failure Detected
         ↓
[Node 1] detect_anomaly      → Scans pipelines, finds failures
         ↓
[Node 2] classify_failure    → Claude AI classifies each failure type
         ↓
[Node 3] investigate_upstream → Maps 9+ downstream systems at risk
         ↓
[Node 4] generate_rca        → Claude AI writes executive RCA report
         ↓
[Node 5] notify_and_save     → Saves report, triggers Slack alert
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent Orchestration | LangGraph (StateGraph) |
| Generative AI | Anthropic Claude API |
| Cloud Data Platform | Snowflake + Azure Data Factory |
| Dashboard | Streamlit |
| Backend | Python + FastAPI |
| CI/CD | GitHub Actions + pytest |
| Infrastructure | Azure (Event Hub, SQL Database) |

---

## Key Results

- Monitors **5 simulated pipelines** modeled after real Azure Data Factory infrastructure
- Detects failures and maps **9 downstream systems** at risk
- Generates complete RCA report in **just a few seconds**
- **5 automated tests** passing via GitHub Actions CI/CD
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

Data pipeline failures are one of the most common and costly problems in data engineering. When a pipeline breaks, an on-call engineer manually digs through logs, traces dependencies, identifies the root cause, and writes an incident report, a process that can take hours while downstream dashboards, reports, and models sit broken.

DataSense AI automates this entire workflow. A LangGraph agent detects failures, uses Claude AI to classify root causes and investigate blast radius, and delivers a professional incident report with no human intervention required.

Same problem every data team faces. Solved with AI.

---

*Built by Sagarika Raju — MS Analytics, University of Southern California*