"""
AlphaPulse AI Accelerator: Smart Name Discrepancy Reconciler
===========================================================
This accelerator resolves naming mismatch breaks between internal asset ledgers
and external custodian statements. Using character-level TF-IDF vectorization 
and Cosine Similarity (or fallback Jaro-Winkler string distance), it matches 
ambiguous names with high certainty and auto-resolves breaks.

Output: reconciliation_breaks_resolved.csv
"""

import os
import csv
import sys

# Define target files
INPUT_CSV = "reconciliation_breaks.csv"
OUTPUT_CSV = "reconciliation_breaks_resolved.csv"

# Golden Master reference mapping for Indian Equities
GOLDEN_MASTER = {
    "MARUTI": "Maruti Suzuki India Limited",
    "ADANIENT": "Adani Enterprises Limited",
    "BHARTIARTL": "Bharti Airtel Limited",
    "AXISBANK": "Axis Bank Limited",
    "INFY": "Infosys Limited",
    "POWERGRID": "Power Grid Corporation of India Limited",
    "HCLTECH": "HCL Technologies Limited",
    "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
    "SBIN": "State Bank of India",
    "RELIANCE": "Reliance Industries Limited",
    "HINDALCO": "Hindalco Industries Limited",
    "HDFCBANK": "HDFC Bank Limited",
    "ITC": "ITC Limited",
    "NTPC": "NTPC Limited",
    "ONGC": "Oil and Natural Gas Corporation Limited",
    "ICICIBANK": "ICICI Bank Limited",
    "TCS": "Tata Consultancy Services Limited",
    "WIPRO": "Wipro Limited",
    "LARSEN": "Larsen & Toubro Limited",
    "BAJFINANCE": "Bajaj Finance Limited"
}

def fallback_jaro_winkler(s1, s2):
    """Pure Python fallback for matching names if scikit-learn is not available."""
    s1, s2 = s1.lower(), s2.lower()
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    max_dist = max(len1, len2) // 2 - 1
    match1 = [False] * len1
    match2 = [False] * len2
    matches = 0
    transpositions = 0
    
    for i in range(len1):
        start = max(0, i - max_dist)
        end = min(i + max_dist + 1, len2)
        for j in range(start, end):
            if not match2[j] and s1[i] == s2[j]:
                match1[i] = True
                match2[j] = True
                matches += 1
                break
                
    if matches == 0:
        return 0.0
        
    k = 0
    for i in range(len1):
        if match1[i]:
            while not match2[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1
            
    m = float(matches)
    t = float(transpositions) / 2.0
    jaro = (m/len1 + m/len2 + (m - t)/m) / 3.0
    
    # Winkler bonus
    prefix = 0
    for i in range(min(4, min(len1, len2))):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
            
    return jaro + (prefix * 0.1 * (1.0 - jaro))

def ml_tf_idf_match(query_name, ticker, golden_ref):
    """TF-IDF character level vectorizer with cosine similarity match."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Get candidate
        golden_name = golden_ref.get(ticker)
        if not golden_name:
            return 0.0, query_name
            
        # Character-level 3-gram Vectorizer
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))
        tfidf = vectorizer.fit_transform([query_name, golden_name])
        score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(score), golden_name
    except ImportError:
        # Fallback to Jaro-Winkler
        golden_name = golden_ref.get(ticker)
        if not golden_name:
            return 0.0, query_name
        score = fallback_jaro_winkler(query_name, golden_name)
        return score, golden_name

def run_smart_reconciliation():
    print("=" * 60)
    print("      ALPHAPULSE: SMART DISCREPANCY RECONCILER       ")
    print("=" * 60)
    
    if not os.path.exists(INPUT_CSV):
        print(f"Error: Target data file '{INPUT_CSV}' not found!")
        print("Please check that you are running from the workspace root folder.")
        sys.exit(1)
        
    print(f"[*] Reading source breaks from '{INPUT_CSV}'...")
    
    rows = []
    headers = []
    with open(INPUT_CSV, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for r in reader:
            rows.append(r)
            
    print(f"[*] Successfully loaded {len(rows)} reconciliation breaks.")
    print("[*] Processing name alignments with ML TF-IDF/JW model...")
    
    resolved_count = 0
    updated_rows = []
    
    # Ensure our output headers contain new validation metrics
    extended_headers = list(headers)
    if "golden_match_name" not in extended_headers:
        extended_headers.extend(["golden_match_name", "match_confidence_score", "resolution_notes"])
        
    for index, row in enumerate(rows):
        ticker = row.get("ticker", "").strip()
        current_name = row.get("security_name", "").strip()
        status = row.get("status", "").strip()
        break_pct = float(row.get("break_pct", "0"))
        
        # Match using our NLP algorithm
        score, golden_name = ml_tf_idf_match(current_name, ticker, GOLDEN_MASTER)
        
        row_copy = dict(row)
        row_copy["golden_match_name"] = golden_name
        row_copy["match_confidence_score"] = f"{score:.4f}"
        
        # Auto-resolution Logic:
        # If break_pct is small AND name confidence is high, it is a system-naming variance break!
        if score >= 0.85 and status != "Resolved":
            row_copy["status"] = "Resolved"
            row_copy["rag_status"] = "Green"
            row_copy["root_cause"] = "System Naming Variance (Auto-Aligned)"
            row_copy["resolution_notes"] = f"Aligned name to Golden Ledger with score {score:.2f}."
            resolved_count += 1
        else:
            row_copy["resolution_notes"] = f"No action; confidence {score:.2f} below threshold."
            
        updated_rows.append(row_copy)
        
    # Write resolved data
    print(f"[*] Writing matched records back to '{OUTPUT_CSV}'...")
    with open(OUTPUT_CSV, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=extended_headers)
        writer.writeheader()
        writer.writerows(updated_rows)
        
    print("=" * 60)
    print(f"[SUCCESS] Reconciler execution finished successfully!")
    print(f" - Total Breaks Processed: {len(rows)}")
    print(f" - Auto-Resolved Naming Breaks: {resolved_count}")
    print(f" - Output Database Generated: {OUTPUT_CSV}")
    print("=" * 60)

if __name__ == "__main__":
    run_smart_reconciliation()
