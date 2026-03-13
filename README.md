# ZAI World Model 🌍🤖
### Macro Market Prediction AI — Historical Data 1800s to Today

---

## What It Does

ZAI World Model downloads **125+ years of financial data** and finds hidden patterns between:
- Oil prices → Stock markets
- Inflation → Crypto crashes  
- Interest rates → Bitcoin cycles
- Dollar strength → Emerging markets

Then compares **today's conditions** to every historical crash since 1929 and predicts what comes next.

---

## How It Works

```
Historical Data (1871-today)
+ Live Market Data (auto-updated)
         ↓
Correlation Engine
(finds: "when X happens → Y follows in N weeks")
         ↓
Pattern Matching
(today looks 78% like 2008 pre-crash)
         ↓
Claude AI Prediction
(4-week, 3-month, 6-month outlook)
         ↓
Live Terminal Dashboard (24/7)
```

---

## Quick Start

### 1. Install
```bash
pip install -r requirements.txt
```

### 2. Add API Key
Edit `config.py`:
```python
ANTHROPIC_KEY = "your-key-here"  # console.anthropic.com
```

### 3. Download Historical Data (once)
```bash
python data_collector.py
```

### 4. Run Analysis
```bash
python correlation_engine.py
```

### 5. Live Dashboard (24/7)
```bash
python dashboard.py
```

---

## Data Sources (All Free)
- **FRED** (Federal Reserve) — Economic data 1871+
- **Yahoo Finance** — Markets 1928+
- **CoinGecko** — Crypto 2010+
- **World Bank** — Global GDP 1960+

---

## Hardware Requirements
- RAM: 8GB minimum
- Storage: 2GB for data
- GPU: Not needed (uses Claude API)
- Python: 3.8+

---

## Files
| File | Purpose |
|------|---------|
| `config.py` | API keys & settings (only file to edit) |
| `data_collector.py` | Downloads all historical data |
| `correlation_engine.py` | Finds patterns + AI prediction |
| `dashboard.py` | Live 24/7 terminal display |

---

*Built by Zawwar — ZAI Trading System*
