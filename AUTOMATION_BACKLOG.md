# AlphaPulse Operational Automation & AI/ML Backlog

This catalog defines the strategic roadmap, backlog items, and proof-of-concept prototypes designed to accelerate operational turnaround, eliminate manual checks, and enforce automated risk controls across the investment data pipeline.

---

## 1. Effort vs. Impact Prioritization Matrix

We group automation opportunities using a standard $2 \times 2$ grid comparing development effort (in weeks/resources) against operational business impact (risk reduction, hours saved, SLA compliance).

```
   HIGH IMPACT  |---------------------------------------------------------|
                |  [Quick Wins - Do Immediately]                          |  [Strategic Investments - Core Projects]
                |  * Item A: Python Smart Match NLP Fuzzy Reconciler       |  * Item D: End-to-end Automated SWIFT Intake  
                |  * Item B: Isolation Forest Price Anomaly Detector     |  * Item E: Multi-Custodian Real-Time API Sync 
                |                                                         |
                |---------------------------------------------------------|---------------------------------------------|
                |  [Low-Hanging Fruit - Fillers]                          |  [Major Long-Term Projects - Review Value]
                |  * Item C: automated daily exception CSV alerts          |  * Item F: Generative Operations Runbook Chatbot
                |                                                         |    using LLMs
   LOW IMPACT   |---------------------------------------------------------|---------------------------------------------|
                                      LOW EFFORT                                             HIGH EFFORT
```

---

## 2. Operational Backlog Catalog

This table indexes all identified automation opportunities with defined business outcomes, effort ratings, impact ratings, owners, and concrete roadmap status.

| ID | Title / Opportunity | Core Description | Business Outcome | Effort (1-5) | Impact (1-5) | Owner / Lead | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **B-01** | **Smart Discrepancy Matcher (TF-IDF)** | Python ML NLP fuzzy-string reconciler to auto-resolve security name discrepancies. | Auto-resolves 80% of naming breaks; reduces manual matching by 4 hours/day. | **1 (Low)** | **5 (High)** | Data Ops Lead | **IMPLEMENTED** (Quick Win Prototype) |
| **B-02** | **Isolation Forest Anomaly Detector** | AI Outlier valuation detection on trades & stale market pricing reference tables. | Flags outliers automatically before NAV calculations; prevents EOD valuation delays. | **1 (Low)** | **5 (High)** | AI Analyst Desk | **IMPLEMENTED** (Quick Win Prototype) |
| **B-03** | **Daily Email Alerts & CSV Summary** | Automated cron script compiling overnight breaks and dispatching active summary to owners. | Replaces manual ticketing reviews; guarantees immediate day-start assignment. | **1 (Low)** | **3 (Medium)**| Systems Lead | **Planned** (Sprint 1) |
| **B-04** | **SWIFT parsing intake automation** | Auto-parsing custodian MT564/MT940 messaging standard to replace CSV uploads. | Removes manual spreadsheet uploads; increases ingestion frequency to real-time. | **3 (Medium)**| **5 (High)** | Operations Dev | **Planned** (Sprint 2) |
| **B-05** | **Real-Time API Sync Hub** | Integration of API endpoints directly to Citi Portal and Bloomberg Terminal feeds. | Obsoletes static file intake entirely; guarantees intraday data freshness. | **4 (High)** | **5 (High)** | Core Platform Dev | **Under Review** |
| **B-06** | **Runbook Intelligent Generative AI** | LLM-driven smart operational assistant that suggests actions based on historic exception comments. | Fast-tracks onboarding training; shortens operational triage time by 30%. | **3 (Medium)**| **4 (High)** | AI Analyst Desk | **Under Review** |

---

## 3. Implemented Quick-Wins / Physical Python Prototypes

To validate the feasibility of this backlog immediately and provide hands-on accelerators, we have deployed two fully-functional Python scripts directly inside this workspace directory. These scripts run on top of standard institutional datasets (`reconciliation_breaks.csv` and `share_prices.csv`).

### Prototype 1: NLP Fuzzy Reconciler (`recon_smart_match.py`)
* **Technology**: Python, `pandas`, `scikit-learn` (TF-IDF Vectorizer & Cosine Similarity).
* **Operation**: Reads your actual `reconciliation_breaks.csv` and runs TF-IDF string character similarity modeling on Custodian security names versus internal Golden store naming. If similarity score exceeds $0.85$, it updates the status of the breaks dynamically, logs execution, and outputs the saved results to `reconciliation_breaks_resolved.csv`.
* **Value**: Saves operations analysts from searching and confirming naming variations manually.

### Prototype 2: Outlier pricing/Valuation Detector (`anomaly_detector.py`)
* **Technology**: Python, `pandas`, `scikit-learn` (Isolation Forest).
* **Operation**: Loads your `share_prices.csv` dataset, extracts close price and stale history features, standardizes using Z-score logic, and fits a scikit-learn Isolation Forest anomaly model (contamination 15%). It flags pricing spikes or suspicious records, prints them to the terminal console, and writes the exceptions log to `share_prices_anomalies_flagged.csv`.
* **Value**: Automatically acts as a risk control to isolate bad pricing values before NAV ledger updates.
