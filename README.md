# AlphaPulse AI Accelerator

## Problem We Are Solving
Financial institutions face significant operational challenges when reconciling data between internal ledgers and external custodian statements, as well as when validating market pricing feeds. Ambiguous naming conventions often lead to "breaks" that require manual intervention. Furthermore, stale or wildly inaccurate pricing data can severely skew Net Asset Value (NAV) calculations if not caught early. This project automates the reconciliation of ambiguous entity names and detects pricing outliers, saving analysts time and drastically reducing operational risk.

## Data Used
We utilized simulated financial datasets representing Indian Equities:
* **Reconciliation Breaks Data (`reconciliation_breaks.csv`):** Contains records of naming mismatches between internal systems and external statements.
* **Share Prices Data (`share_prices.csv`):** Daily closing prices for various tickers, containing simulated anomalies such as stale feeds, missing values, and extreme price deviations.
* **Golden Master Reference:** An internal mapping dictionary of official asset names used for matching (e.g., matching "MARUTI" to "Maruti Suzuki India Limited").

## Our Approach
The accelerator utilizes a dual-engine approach to solve these data quality and reconciliation issues:

1. **Smart Name Discrepancy Reconciler:**
   Resolves naming mismatch breaks using NLP. We employ a character-level TF-IDF vectorizer (n-grams 2-4) combined with Cosine Similarity to calculate confidence scores between the broken records and a Golden Master reference. If the confidence score is 0.85 or higher, the system auto-resolves the break as a "System Naming Variance". A pure Python Jaro-Winkler string distance algorithm serves as a robust fallback.
   
2. **Pricing Outlier & Valuation Anomaly Detector:**
   Identifies suspicious market data, stale feeds, and extreme valuation deviations before NAV ledgers update. We apply a multivariate Isolation Forest Machine Learning model (via scikit-learn) with a ~5% contamination rate on features like `close_price` and `days_stale`. As a fallback, the engine uses a statistical rolling Z-score threshold (flagging anything beyond 2.5 standard deviations).

## Concrete Findings & Results
* **Automated Reconciliation:** Processed a dataset of 300 reconciliation breaks and successfully auto-resolved 13 ambiguous naming discrepancy breaks with high confidence, updating the ledger without manual review.
* **Anomaly Detection:** Analyzed 2,000 share price records and successfully flagged 172 anomalies, rapidly pinpointing missing values, statistical valuation outliers, and highly stale pricing feeds.
