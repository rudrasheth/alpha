# AlphaPulse Standardized Priority SOP Pack
## Document Version Control & Governance
* **Status**: Published / Under Version Control
* **Agreed Repository**: Git / Confluence / SharePoint (Operations Space)
* **Target Audience**: Data Operations, Reconciliation Specialists, Ref Data Analyst, and Analytics Teams

| Version | Date | Author | Description of Change | Approved By | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| v1.0.0 | 2026-05-27 | Operations Lead & AI Partners | Initial Standardization of Priority SOPs with RACI, SLAs, and Python Controls | Global Operations Head | Approved |

---

## SOP-01: Position Reconciliation Breaks Resolution

### 1.1 Business Outcome
Ensure zero discrepancy in position holdings between external Custodian statements (Citi, Deutsche Bank, BNP Paribas, JPMorgan) and the internal Golden Source ledger by EOD to guarantee accurate Net Asset Value (NAV) valuation and prevent regulatory reporting breaches.

### 1.2 RACI Matrix
* **Responsible (R)**: Data Ops Intern (Smart Match & Triage)
* **Accountable (A)**: Operations Manager (Approval of manual adjustments)
* **Consulted (C)**: Custody Settlements Desk, Fund Accounting Team
* **Informed (I)**: Client Relations & Compliance Lead

### 1.3 Service Level Agreement (SLA) & Escalation
* **Standard Resolution Window**: 4 Hours from feed ingestion.
* **Escalation Path**:
  * **Level 1 (T+2 Hours)**: Operational Specialist alerts Custody settlements desk.
  * **Level 2 (T+3 Hours)**: Escalated to Lead Custody Analyst for high-severity breaks (> ₹1,000,000 INR variance).
  * **Level 3 (T+4 Hours)**: Escalated to VP Fund Administration and Portfolio Manager (Manual override or trade halt consideration).

### 1.4 Step-by-Step Workflow & Automated Controls
1. **Feed Ingestion**: External custodian CSV files are fetched and compared with internal Ledger records.
2. **Dynamic Check & TF-IDF Cosine Similarity Control**:
   * *Control 1*: Match securities via standard identifiers (ISIN/CUSIP/SEDOL).
   * *Control 2 (Fuzzy Text Matching)*: For naming breaks (e.g. "TCS" vs "Tata Consultancy Services"), run the python fuzzy matcher to calculate Cosine Similarity. If similarity is $\ge 0.85$, auto-resolve the naming discrepancy.
3. **Investigation & Action**:
   * If variance is a volume mismatch, identify whether it's an unposted trade, double-entry, or trade execution failure.
   * If volume is verified, update matching status in Ledger and log manual reconciliation action with unique auditor ID.
4. **Acceptance Validation & Verification Criteria**:
   * 100% of reconciliations with variance < 0.01% are auto-matched.
   * All unresolved breaks have active ticket logs with documented comments.
   * Total outstanding reconciliation variance must be ₹0.00 before final EOD sign-off.

---

## SOP-02: Trade Quality Exception & Smart Triage

### 2.1 Business Outcome
Identify, classify, and resolve data quality anomalies (duplicated trades, invalid prices, missing broker codes, and size outliers) in trade execution feeds within 2 hours of ingestion to ensure clean data reaches down-stream ledger storage and risk reporting systems.

### 2.2 RACI Matrix
* **Responsible (R)**: Data Ops Intern (Intelligent routing and verification)
* **Accountable (A)**: Data Lead Analyst (Execution & final processing)
* **Consulted (C)**: Broker Confirmations Desk, Trade Desk Systems Analyst
* **Informed (I)**: Fund Accounting Unit, Risk Compliance Officer

### 2.3 Service Level Agreement (SLA) & Escalation
* **Standard Resolution Window**: 2 Hours.
* **Escalation Path**:
  * **Level 1 (T+30 Min)**: Auto-ticket raised in exceptions manager and routed to Data Ops.
  * **Level 2 (T+60 Min)**: Escaled to Trade Desk Systems Analyst for schema corrections or broker re-feed requests.
  * **Level 3 (T+120 Min)**: Global Head of Support notified if critical trade feed is halted.

### 2.4 Step-by-Step Workflow & Automated Controls
1. **Schema Validation Check**: Perform strict numeric bounds checking on Trade Quantity and Price.
2. **Isolation Forest Machine Learning Outlier Detection**:
   * Run Isolation Forest python accelerator to score trades. Anomalies (outlier quantities, 3-sigma pricing spikes) are flagged automatically.
3. **Automated Triage Routing**:
   * High-severity price exceptions are routed to the Ref Data Desk.
   * Quantity exceptions and duplications are routed to the Broker Confirmations Desk.
4. **Acceptance Validation & Verification Criteria**:
   * Zero duplicate trades allowed in the Golden Store.
   * No trade record may possess null values in core columns (ISIN, Quantity, Price, Client, Broker).
   * All exceptions resolved and pushed to "Resolved" status before downstream integration.

---

## SOP-03: Security Reference Master Validation

### 3.1 Business Outcome
Audit and clean all reference master records (missing ISINs, stale market prices, incorrect sector classifications) before EOD NAV valuation run to ensure portfolio performance reporting is based on verified security profiles.

### 3.2 RACI Matrix
* **Responsible (R)**: Data Ops Intern (Data verification & audit)
* **Accountable (A)**: Reference Master Analyst (Updates approval)
* **Consulted (C)**: Compliance & Risk Officer
* **Informed (I)**: Investment Operations Team, Downstream Performance Consumers

### 3.3 Service Level Agreement (SLA) & Escalation
* **Standard Resolution Window**: EOD (Cutoff at 6:00 PM IST).
* **Escalation Path**:
  * **Level 1 (4:00 PM IST)**: Reference Master Lead notified of unmapped assets.
  * **Level 2 (5:00 PM IST)**: VP Fund Administration notified of potential NAV calculation delay.
  * **Level 3 (5:30 PM IST)**: Executive Risk Committee alerted if critical asset pricing is missing.

### 3.4 Step-by-Step Workflow & Automated Controls
1. **Exchange Feed Verification**: Compare active assets against NSE/BSE and Bloomberg Reference Master Feeds.
2. **Automated Integrity Checks**:
   * *ISIN Check*: Validate ISIN character length (12 characters) and standard format.
   * *Staleness Check*: Flag price records with `days_stale > 1` as anomalies.
3. **Remediation**:
   * Manually override wrong sector categories using official exchange classification.
   * Query database for missing ISINs and merge duplicate profiles.
4. **Acceptance Validation & Verification Criteria**:
   * 100% of reference records must contain a valid, registered ISIN.
   * Stale pricing flags must be resolved (either refreshed or manually approved with source quote PDF).
   * Reference data audit log displays timestamp, changes made, and approving analyst ID.
