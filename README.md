# DataSense AI

![CI](https://github.com/saga0302/datasense-ai/actions/workflows/ci.yml/badge.svg)

**AI-Powered Data Reliability Platform with Conversational Analyst**

> DataSense AI monitors real Instacart e-commerce pipeline data, detects anomalies using unsupervised machine learning, and generates executive-grade incident reports — all accessible through a conversational analyst you can query in plain English.

**[Live Demo](https://datasense-ai-mkpy6qfcyxvamtvnvhyzxv.streamlit.app)**

---

## What It Does

1. **Ingests** — Real Instacart US grocery orders: 131,209 orders across 4 joined tables, feature-engineered into 14 behavioral signals including personal deviation baselines
2. **Detects** — Isolation Forest unsupervised ML scores every order by anomaly level — no fake labels, no hardcoded rules, thresholds derived from data distribution
3. **Monitors** — LangGraph agent scans 4 time-based pipeline batch runs, flags any batch where average anomaly score exceeds 0.35 threshold
4. **Classifies** — Claude AI classifies each failure with RAG retrieving similar past incidents from ChromaDB vector store
5. **Scores** — ML node runs Isolation Forest on detected anomalies, adds anomaly score and top driving features to agent state
6. **Investigates** — MCP server exposes pipeline diagnostic tools; agent maps upstream sources and downstream blast radius across dependent systems
7. **Reports** — Claude generates professional RCA report combining ML evidence with AI reasoning — financial exposure, root cause hypotheses, prioritised remediation steps
8. **Answers** — Conversational analyst lets you query pipelines, orders, trends, and predictions in plain English with interactive charts

---

## Architecture

```
Real Instacart Data (3.4M orders → 131,209 with complete product detail)
↓
Isolation Forest ML Model (unsupervised — learns normality, no labels needed)
↓
[Node 1]   detect_anomaly       → Scans 4 time-based batch pipeline runs
↓
[Node 2]   classify_failure     → Claude AI + RAG (ChromaDB historical incidents)
↓
[Node 2.5] ml_score_severity    → Isolation Forest scores each anomaly 0→1
↓
[Node 3]   investigate_upstream → Maps upstream sources + downstream blast radius
↓
[Node 4]   generate_rca         → Claude writes RCA with ML evidence + reasoning
↓
[Node 5]   notify_and_save      → Saves .md + .json report, triggers Slack alert
↓
Conversational Analyst           → Ask anything in plain English with charts
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent Orchestration | LangGraph (StateGraph) |
| Generative AI | Anthropic Claude API (claude-opus-4-6) |
| ML Anomaly Detection | Isolation Forest (scikit-learn) |
| Agent Tool Protocol | Model Context Protocol (MCP) |
| Vector Store / RAG | ChromaDB |
| Data Engineering | Pandas, NumPy |
| Visualisation | Plotly |
| Dashboard | Streamlit (multipage) |
| CI/CD | GitHub Actions + pytest |
| Deployment | Streamlit Cloud |

---

## Dataset

**Instacart Market Basket Dataset** — real US grocery orders, publicly released by Instacart on Kaggle.

| Table | Rows | Used for |
|-------|------|---------|
| orders.csv | 3,421,083 | Order metadata, timing, user history |
| order_products__train.csv | 1,384,617 | Product detail, reorder flags |
| products.csv | 49,688 | Product to aisle mapping |
| aisles.csv | 134 | Aisle name lookup |

**Engineered features (14 total):**
- `cart_size`, `reorder_rate`, `unique_departments` — order-level signals
- `cart_deviation`, `reorder_deviation`, `days_deviation` — deviation from each user's personal baseline
- `order_hour_anomaly`, `is_first_order` — risk flags
- `user_total_orders`, `user_avg_reorder`, `user_avg_cart` — user-level context

---

## ML Model

**Isolation Forest** — same family of algorithms as AWS SageMaker Random Cut Forest, used in production at Amazon for anomaly detection.

- No labels required — learns what normal looks like from 131,209 real orders
- Outputs continuous anomaly score 0→1 per order
- Thresholds derived from score distribution (not hardcoded):
  - CRITICAL ≥ 0.488 (top 5% — 6,561 orders)
  - HIGH ≥ 0.279 (top 20% — 19,681 orders)
  - MEDIUM ≥ 0.181 (top 40% — 26,242 orders)
  - LOW < 0.181 (bottom 60% — 78,725 orders)
- Most anomalous order: order_id 2008596 — score 1.0, cart size 46 items, placed 4am

---

## Pipeline Batch Monitoring

Orders are split into 4 time-based pipeline runs. Each batch is evaluated against the anomaly threshold:

| Batch | Time Window | Orders | Status |
|-------|------------|--------|--------|
| instacart_earlymorning_batch | 12am – 5am | 2,507 | FAILED (avg score 0.431) |
| instacart_morning_batch | 6am – 11am | ~35,000 | SUCCESS |
| instacart_afternoon_batch | 12pm – 5pm | ~52,000 | SUCCESS |
| instacart_evening_batch | 6pm – 11pm | ~41,000 | SUCCESS |

---

## Conversational Analyst

A second Streamlit page where you query your pipeline data in plain English:

- *"What happened in the latest run?"* → severity distribution chart + Claude summary
- *"How many orders in each batch?"* → bar chart with exact counts per time window
- *"Tell me about order 2008596"* → full feature breakdown from scored_orders.csv
- *"Show me the trend by hour"* → line chart with failure threshold line
- *"Which time window is worst?"* → comparison chart + business impact
- *"Predict tomorrow's risk"* → gauge chart + risk reasoning
- *"What does the incident report say?"* → Claude reads saved report and answers
- *"Scan pipelines now"* → full 6-node LangGraph agent fires with RAG + ML

**MCP Status:** Runs as subprocess locally (🟢 active). On Streamlit Cloud automatically switches to direct API mode (🔵) — same data, different transport layer.

---

## Key Results

- **131,209** real Instacart US orders processed and scored by Isolation Forest
- **6,561** orders flagged CRITICAL (5%) — no labels, purely data-driven
- **1 of 4** pipeline batch windows failed (early morning: avg score 0.431 > 0.35 threshold)
- **3** downstream systems at risk per failed pipeline
- **Top anomalous order** scored 1.0 — 46-item cart placed at 4am, consistent with bot/fraud pattern
- Full executive RCA report generated in under 60 seconds including ML evidence and financial exposure
- **6** automated tests passing via GitHub Actions CI/CD

---

## Running Locally
```bash
# Clone and setup
git clone https://github.com/saga0302/datasense-ai.git
cd datasense-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Download Instacart dataset from Kaggle
# Place these 4 files in data/instacart/:
# orders.csv, order_products__train.csv, products.csv, aisles.csv

# Run the data pipeline and train ML model
python data/instacart_pipeline.py
python models/train_severity.py

# Launch the dashboard
streamlit run dashboard.py
```

---

## Running Tests
```bash
python -m pytest tests/ -v
```

---

## Running the Agent Directly
```bash
python main.py
```

---

## Real-World Context

Data pipeline failures are one of the most costly problems in data engineering. When a batch pipeline fails, engineers manually dig through logs, trace dependencies, identify root cause, and write incident reports — a process that takes hours while downstream dashboards and models run on stale data.

DataSense AI automates this entire workflow using real e-commerce transaction data. An Isolation Forest model trained on 131,209 real Instacart orders detects which pipeline batches are genuinely anomalous. A LangGraph agent then classifies failures using Claude AI with RAG-retrieved historical context, maps the downstream blast radius through MCP tools, and delivers a professional RCA report in under 60 seconds. A conversational analyst lets any stakeholder query the data in plain English — no SQL, no dashboards, just questions and answers.

Same problem every data team faces. Solved with real data, real ML, and real AI.

---

*Built by Sagarika Raju — MS Analytics, University of Southern California*
