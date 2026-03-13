"""
ZAI World Model - Correlation & Pattern Engine
Historical patterns dhundta hai
Example: "Jab oil 20% upar gaya + inflation high thi = market crash aya"
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DATA_PATH, ANTHROPIC_KEY

# ============================================================
# LOAD ALL DATA
# ============================================================
def load_all_data():
    """Saari downloaded CSV files load karo"""
    data = {}
    historical_path = f"{DATA_PATH}/historical"
    
    if not os.path.exists(historical_path):
        print("❌ Data nahi mila! Pehle data_collector.py chalao")
        return {}
    
    for file in os.listdir(historical_path):
        if file.endswith(".csv"):
            name = file.replace(".csv", "")
            try:
                df = pd.read_csv(f"{historical_path}/{file}", parse_dates=["date"])
                df = df.sort_values("date").set_index("date")
                data[name] = df["value"]
                print(f"  ✅ Loaded {name}: {len(df)} records")
            except Exception as e:
                print(f"  ❌ {name}: {e}")
    
    return data

def merge_data(data_dict):
    """Sab series ko ek DataFrame mein merge karo"""
    if not data_dict:
        return pd.DataFrame()
    
    # Remove empty series
    data_dict = {k: v for k, v in data_dict.items() if len(v) > 0}
    
    df = pd.DataFrame(data_dict)
    
    # DatetimeIndex ensure karo
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    
    # Weekly resample
    df = df.resample("W").last()
    df = df.ffill()
    
    return df

# ============================================================
# CORRELATION FINDER
# ============================================================
def find_correlations(df):
    """Har cheez ka dusri cheez se correlation nikalo"""
    if df.empty:
        return {}
    
    # Percentage change calculate karo (price ki jagah change zyada meaningful)
    pct = df.pct_change(4)  # 4-week change
    
    corr_matrix = pct.corr()
    
    correlations = {}
    cols = corr_matrix.columns.tolist()
    
    for i, col1 in enumerate(cols):
        for col2 in cols[i+1:]:
            corr = corr_matrix.loc[col1, col2]
            if not np.isnan(corr):
                correlations[f"{col1}_vs_{col2}"] = round(corr, 3)
    
    # Sort by absolute correlation
    correlations = dict(sorted(correlations.items(), 
                               key=lambda x: abs(x[1]), reverse=True))
    
    return correlations

def find_lead_lag_relationships(df, max_lag_weeks=12):
    """
    Kaunsi cheez aage chalti hai kaunsi ke?
    Example: Oil price 8 hafton baad inflation affect karti hai
    """
    relationships = []
    cols = df.columns.tolist()
    pct = df.pct_change(4)
    
    for leader in cols:
        for follower in cols:
            if leader == follower:
                continue
            
            best_corr = 0
            best_lag = 0
            
            for lag in range(1, max_lag_weeks + 1):
                try:
                    corr = pct[leader].corr(pct[follower].shift(-lag))
                    if abs(corr) > abs(best_corr):
                        best_corr = corr
                        best_lag = lag
                except:
                    continue
            
            if abs(best_corr) > 0.4:  # 40%+ correlation
                relationships.append({
                    "leader": leader,
                    "follower": follower,
                    "lag_weeks": best_lag,
                    "correlation": round(best_corr, 3),
                    "direction": "same" if best_corr > 0 else "opposite"
                })
    
    # Sort by strength
    relationships.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return relationships[:50]  # Top 50 relationships

# ============================================================
# HISTORICAL CRASH PATTERN FINDER
# ============================================================
KNOWN_CRASHES = {
    "Great Depression 1929": ("1928-01-01", "1933-01-01"),
    "Oil Crisis 1973": ("1972-01-01", "1975-01-01"),
    "Black Monday 1987": ("1987-06-01", "1988-06-01"),
    "Dot-com Crash 2000": ("1999-01-01", "2002-12-01"),
    "Financial Crisis 2008": ("2007-01-01", "2009-12-01"),
    "COVID Crash 2020": ("2020-01-01", "2020-12-01"),
    "Crypto Crash 2022": ("2021-11-01", "2022-12-01"),
}

def extract_crash_patterns(df):
    """
    Har crash se pehle kya conditions thi — ye patterns nikalo
    Ye future prediction ke liye use hongi
    """
    patterns = {}
    
    for crash_name, (start, end) in KNOWN_CRASHES.items():
        try:
            # Crash se 6 mahine pehle ka data
            pre_start = pd.to_datetime(start) - timedelta(weeks=26)
            pre_end = pd.to_datetime(start)
            
            pre_crash = df.loc[pre_start:pre_end]
            
            if pre_crash.empty:
                continue
            
            # Kya kya ho raha tha crash se pehle
            pattern = {"crash": crash_name, "period": start}
            
            for col in df.columns:
                if col in pre_crash.columns:
                    series = pre_crash[col].dropna()
                    if len(series) > 4:
                        total_change = ((series.iloc[-1] - series.iloc[0]) / 
                                       abs(series.iloc[0])) * 100
                        pattern[f"{col}_change_pct"] = round(total_change, 2)
            
            patterns[crash_name] = pattern
            
        except Exception as e:
            continue
    
    return patterns

# ============================================================
# CURRENT CONDITIONS vs HISTORICAL
# ============================================================
def compare_current_to_history(df, crash_patterns):
    """
    Aaj ke conditions ko historical crashes se compare karo
    Return: Kaunse crash se sabse zyada milta hai aaj ka scenario
    """
    if df.empty or not crash_patterns:
        return []
    
    # Last 6 months ki current conditions
    six_months_ago = datetime.now() - timedelta(weeks=26)
    current = df.loc[six_months_ago:]
    
    if current.empty:
        return []
    
    current_changes = {}
    for col in df.columns:
        if col in current.columns:
            series = current[col].dropna()
            if len(series) > 2:
                change = ((series.iloc[-1] - series.iloc[0]) / 
                         abs(series.iloc[0])) * 100
                current_changes[col] = round(change, 2)
    
    # Har historical pattern se similarity calculate karo
    similarities = []
    
    for crash_name, pattern in crash_patterns.items():
        score = 0
        matches = 0
        details = []
        
        for col in current_changes:
            hist_key = f"{col}_change_pct"
            if hist_key in pattern:
                curr_val = current_changes[col]
                hist_val = pattern[hist_key]
                
                # Same direction?
                if (curr_val > 0 and hist_val > 0) or (curr_val < 0 and hist_val < 0):
                    score += 1
                    matches += 1
                    details.append(f"{col}: now {curr_val:+.1f}% vs history {hist_val:+.1f}%")
        
        if matches > 0:
            similarity_pct = (score / matches) * 100
            similarities.append({
                "crash": crash_name,
                "similarity_pct": round(similarity_pct, 1),
                "matching_indicators": matches,
                "details": details[:5]  # Top 5 details
            })
    
    similarities.sort(key=lambda x: x["similarity_pct"], reverse=True)
    return similarities

# ============================================================
# CLAUDE AI PREDICTION
# ============================================================
def get_ai_prediction(correlations, relationships, similarities, current_data):
    """Claude ko sab data do, prediction lo"""
    
    import requests as req
    
    # Top correlations
    top_corr = dict(list(correlations.items())[:15])
    
    # Top relationships
    top_rel = relationships[:10]
    
    # Most similar crash
    top_similar = similarities[:3] if similarities else []
    
    # Current market snapshot
    live_path = f"{DATA_PATH}/live/latest.json"
    live_data = {}
    if os.path.exists(live_path):
        with open(live_path) as f:
            live_data = json.load(f)
    
    prompt = f"""You are ZAI - a macro market prediction AI with access to historical data from 1800s to today.

HISTORICAL CORRELATIONS FOUND (top relationships):
{json.dumps(top_corr, indent=2)}

LEAD-LAG RELATIONSHIPS (X happens N weeks before Y):
{json.dumps(top_rel, indent=2)}

CURRENT CONDITIONS vs HISTORICAL CRASHES:
{json.dumps(top_similar, indent=2)}

CURRENT LIVE MARKET DATA:
{json.dumps(live_data, indent=2)}

Based on ALL this data, provide your market prediction.

Consider:
1. Which historical period does today most resemble?
2. What typically happens next based on these patterns?
3. What are the key warning signals or positive signals?
4. What is your prediction for next 4 weeks, 3 months, 6 months?

Respond in this EXACT JSON format:
{{
  "current_era_similarity": "which historical period this most resembles",
  "overall_market_outlook": "BULLISH/BEARISH/NEUTRAL/VOLATILE",
  "confidence": 0-100,
  "key_signals": ["signal1", "signal2", "signal3"],
  "warning_signs": ["warning1", "warning2"],
  "positive_signs": ["positive1", "positive2"],
  "predictions": {{
    "4_weeks": {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "..."}},
    "3_months": {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "..."}},
    "6_months": {{"direction": "UP/DOWN/SIDEWAYS", "magnitude": "X%", "reasoning": "..."}}
  }},
  "crypto_specific": {{"outlook": "...", "key_driver": "..."}},
  "most_important_indicator_to_watch": "...",
  "summary": "2-3 sentence summary in simple language"
}}"""

    try:
        response = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        
        result = response.json()
        text = result["content"][0]["text"]
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
        
    except Exception as e:
        print(f"❌ Claude prediction error: {e}")
        return None

# ============================================================
# SAVE RESULTS
# ============================================================
def save_analysis(correlations, relationships, crash_patterns, similarities, prediction):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    analysis = {
        "generated_at": datetime.now().isoformat(),
        "top_correlations": dict(list(correlations.items())[:20]),
        "lead_lag_relationships": relationships[:20],
        "crash_patterns_found": len(crash_patterns),
        "current_similarity": similarities[:5] if similarities else [],
        "ai_prediction": prediction
    }
    
    path = f"{DATA_PATH}/predictions/analysis_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Latest prediction file (dashboard ke liye)
    latest_path = f"{DATA_PATH}/predictions/latest.json"
    with open(latest_path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"✅ Analysis saved: {path}")
    return analysis

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("🧠 ZAI CORRELATION ENGINE")
    print("="*60)
    
    if ANTHROPIC_KEY == "YOUR_ANTHROPIC_API_KEY_HERE":
        print("❌ config.py mein Anthropic API key daalo pehle!")
        exit()
    
    print("\n📂 Data load kar raha hun...")
    data = load_all_data()
    
    if not data:
        print("❌ Koi data nahi mila. Pehle: python data_collector.py")
        exit()
    
    print(f"\n✅ {len(data)} datasets loaded")
    
    print("\n🔗 Data merge kar raha hun...")
    df = merge_data(data)
    print(f"   Combined shape: {df.shape}")
    
    print("\n📊 Correlations calculate kar raha hun...")
    correlations = find_correlations(df)
    print(f"   {len(correlations)} correlations found")
    
    print("\n⏱️ Lead-lag relationships dhundh raha hun...")
    relationships = find_lead_lag_relationships(df)
    print(f"   {len(relationships)} relationships found")
    
    print("\n💥 Historical crash patterns extract kar raha hun...")
    crash_patterns = extract_crash_patterns(df)
    print(f"   {len(crash_patterns)} crash patterns analyzed")
    
    print("\n🔍 Current conditions compare kar raha hun...")
    similarities = compare_current_to_history(df, crash_patterns)
    if similarities:
        print(f"   Most similar to: {similarities[0]['crash']} ({similarities[0]['similarity_pct']}%)")
    
    print("\n🤖 Claude se prediction le raha hun...")
    prediction = get_ai_prediction(correlations, relationships, similarities, df)
    
    if prediction:
        print(f"\n{'='*60}")
        print("📋 ZAI PREDICTION:")
        print(f"   Outlook: {prediction.get('overall_market_outlook')}")
        print(f"   Confidence: {prediction.get('confidence')}%")
        print(f"   Similar to: {prediction.get('current_era_similarity')}")
        print(f"   Summary: {prediction.get('summary')}")
        print(f"{'='*60}")
    
    analysis = save_analysis(correlations, relationships, crash_patterns, similarities, prediction)
    print("\n✅ Complete! Dashboard chalao: python dashboard.py")
