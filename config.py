# ============================================================
# ZAI WORLD MODEL - CONFIG
# SIRF YE FILE EDIT KARO - KUCH AUR MAT CHHEDNA
# ============================================================

# Anthropic API Key (console.anthropic.com se lo)
ANTHROPIC_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"
# Data storage path (apna 1TB SSD path daalo)
# Windows example: "D:/ZAI_Data"
# Linux example: "/mnt/ssd/ZAI_Data"
DATA_PATH = "./zai_data"

# Kitne saal pehle se data chahiye (1800 minimum)
HISTORY_FROM_YEAR = 1871

# Live update interval (seconds)
UPDATE_INTERVAL = 300  # har 5 minute mein update

# Prediction confidence threshold
MIN_CONFIDENCE = 65  # 65% se kam pe predict mat karo

# ============================================================
# DATASETS TO DOWNLOAD (True/False)
# ============================================================
DATASETS = {
    "sp500":        True,   # S&P 500 (1928 se)
    "gold":         True,   # Gold prices (1970 se)
    "oil":          True,   # Crude oil (1946 se)
    "dollar":       True,   # Dollar index (1971 se)
    "bitcoin":      True,   # Bitcoin (2010 se)
    "inflation":    True,   # US CPI (1871 se)
    "gdp":          True,   # US GDP (1929 se)
    "unemployment": True,   # US Unemployment (1948 se)
    "interest":     True,   # Fed interest rates (1954 se)
    "vix":          True,   # Fear index (1990 se)
    "nasdaq":       True,   # Nasdaq (1971 se)
    "dxy":          True,   # Dollar index detailed
    "bonds":        True,   # 10Y Treasury yield (1962 se)
    "copper":       True,   # Copper (economic indicator)
    "crypto_total": True,   # Total crypto market cap
}
