"""
AlphaPulse AI Accelerator: Pricing Outlier & Valuation Anomaly Detector
======================================================================
This accelerator identifies suspicious market data records, stale pricing feeds, 
and extreme valuation deviations in stock close prices before NAV ledgers update.
It uses an Isolation Forest ML model (or statistical rolling Z-score fallback) 
to isolate valuation anomalies.

Output: share_prices_anomalies_flagged.csv
"""

import os
import csv
import sys
import math

INPUT_CSV = "share_prices.csv"
OUTPUT_CSV = "share_prices_anomalies_flagged.csv"

def parse_float(val):
    """Safely converts string value to float or returns None."""
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None

def detect_zscore_outliers(prices):
    """Fallback statistical anomaly detector using mean and standard deviation."""
    # Filter valid close prices
    valid_prices = [p for p in prices if p['close_price'] is not None]
    if len(valid_prices) < 5:
        return [] # Too few elements to compute statistics
        
    close_vals = [p['close_price'] for p in valid_prices]
    mean_val = sum(close_vals) / len(close_vals)
    
    # Calculate Standard Deviation
    variance = sum((x - mean_val) ** 2 for x in close_vals) / len(close_vals)
    std_dev = math.sqrt(variance) if variance > 0 else 1.0
    
    anomalies = []
    for record in prices:
        c_price = record['close_price']
        is_stale = record['days_stale'] > 5
        
        if c_price is None:
            # Missing prices are data quality anomalies
            record['anomaly_score'] = 1.0
            record['is_anomaly'] = "True"
            record['anomaly_type'] = "Missing Value Break"
            anomalies.append(record)
        else:
            z_score = abs(c_price - mean_val) / std_dev
            # Threshold of 2.5 standard deviations or highly stale records
            if z_score > 2.5 or is_stale:
                record['anomaly_score'] = min(1.0, z_score / 4.0)
                record['is_anomaly'] = "True"
                record['anomaly_type'] = "Valuation Outlier (Z-Score)" if z_score > 2.5 else "Stale Feed Anomaly"
                anomalies.append(record)
            else:
                record['anomaly_score'] = z_score / 4.0
                record['is_anomaly'] = "False"
                record['anomaly_type'] = "Normal"
                
    return anomalies

def detect_ml_outliers(prices):
    """Multivariate Isolation Forest anomaly detector from scikit-learn."""
    try:
        import pandas as pd
        
        # pyrefly: ignore [missing-import]
        import numpy as np
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        
        # Load records to DataFrame
        df = pd.DataFrame(prices)
        
        # Impute missing close prices with average close price
        avg_close = df['close_price'].mean(skipna=True)
        df['close_price_filled'] = df['close_price'].fillna(avg_close)
        
        # Features for Isolation Forest
        X = df[['close_price_filled', 'days_stale']].values
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit Isolation Forest (Contamination set to ~5%)
        model = IsolationForest(contamination=0.05, random_state=42)
        preds = model.fit_predict(X_scaled)
        decision_scores = model.decision_function(X_scaled)
        
        anomalies = []
        for i, row in df.iterrows():
            record = prices[i]
            record['anomaly_score'] = float(-decision_scores[i]) # Higher means more anomalous
            
            # Predict labels (-1 is outlier, 1 is inlier)
            if preds[i] == -1 or record['close_price'] is None:
                record['is_anomaly'] = "True"
                record['anomaly_type'] = "ML Isolation Forest Outlier" if record['close_price'] is not None else "Missing Value Break"
            else:
                record['is_anomaly'] = "False"
                record['anomaly_type'] = "Normal"
            anomalies.append(record)
            
        return anomalies
        
    except ImportError:
        # Fall back to statistical Z-score
        return detect_zscore_outliers(prices)

def run_anomaly_detection():
    print("=" * 60)
    print("     ALPHAPULSE: PRICING OUTLIER ANOMALY DETECTOR     ")
    print("=" * 60)
    
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Target data file '{INPUT_CSV}' not found!")
        print("Please check that you are running from the workspace root folder.")
        sys.exit(1)
        
    print(f"[*] Reading market prices from '{INPUT_CSV}'...")
    
    records = []
    headers = []
    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for r in reader:
            parsed = dict(r)
            parsed['close_price'] = parse_float(r.get('close_price'))
            parsed['days_stale'] = int(r.get('days_stale', '0') or 0)
            records.append(parsed)
            
    print(f"[*] Loaded {len(records)} price records.")
    print("[*] Running pricing anomaly model...")
    
    # Process outliers per ticker to make the detection group-aware
    tickers = set(r['ticker'] for r in records)
    print(f"[*] Processing anomalies across {len(tickers)} distinct tickers...")
    
    processed_records = []
    
    for t in tickers:
        ticker_records = [r for r in records if r['ticker'] == t]
        # Detect outliers in this subset
        flagged = detect_ml_outliers(ticker_records)
        processed_records.extend(flagged)
        
    anomaly_count = sum(1 for r in processed_records if r['is_anomaly'] == "True")
    
    # Write flagged database to CSV
    extended_headers = list(headers)
    if "is_anomaly" not in extended_headers:
        extended_headers.extend(["anomaly_score", "is_anomaly", "anomaly_type"])
        
    print(f"[*] Exporting flagged database to '{OUTPUT_CSV}'...")
    with open(OUTPUT_CSV, mode='w', encoding='utf-8', newline='') as f:
        # We need to output the original float/string value of close price safely
        writer = csv.DictWriter(f, fieldnames=extended_headers)
        writer.writeheader()
        
        # Formatting outputs back to original strings before writing
        for r in processed_records:
            row_out = dict(r)
            if r['close_price'] is None:
                row_out['close_price'] = ""
            row_out['anomaly_score'] = f"{r['anomaly_score']:.4f}"
            writer.writerow(row_out)
            
    print("=" * 60)
    print(f"[SUCCESS] Valuation Outlier detection completed successfully!")
    print(f" - Total Price Records Analyzed: {len(records)}")
    print(f" - Valuation/Stale Anomalies Flagged: {anomaly_count}")
    print(f" - Output Database Generated: {OUTPUT_CSV}")
    print("=" * 60)

if __name__ == "__main__":
    run_anomaly_detection()
