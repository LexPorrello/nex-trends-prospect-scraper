# Nex-Trends Prospect Scraper

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/badge/GitHub-LexPorrello%2Fnex--trends--prospect--scraper-lightgrey.svg)](https://github.com/LexPorrello/nex-trends-prospect-scraper)

Nex-Trends Prospect Scraper — Surface high-value local businesses across any vertical (Auto Repair, Chiropractic, Law, Dental, Real Estate) that are missing obvious marketing infrastructure.

## 📋 What This Does

Finds businesses with clear, addressable gaps in their digital presence that Nex-Trends can fix:
- **Scans** any target vertical across your Las Vegas metro corridor
- **Gap Detection** — checks for missing website, no chat widget, no SSL, no booking system, missing Facebook page
- **Opportunity Scoring** — 0-10 based on gap severity
- **Custom Profiles** — per-vertical templates (auto repair shops vs chiropractors need different audits)
- **Routes** HOT/WARM opportunities to Hermes scoring engine via webhook

## 🏗️ Architecture

```
src/
├── detectors/
│   └── gap_detector.py     # Multi-layer gap detection scoring
├── analyzers/
│   └── __init__.py         # Per-vertical audit templates (expandable)
├── exporters/
│   └── __init__.py         # CSV/JSON export
└── main.py                 # CLI: discover, report, export
```

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Discover opportunities across all verticals
python src/main.py discover

# Or target one vertical
python src/main.py discover --vertical "Auto Repair" --market "Las Vegas, NV"

# Export to CSV for GHL import
python src/main.py export --tier HOT
```

## 🔑 Gap Detection Scoring (0-10)

| Gap | Points | Description |
|-----|--------|-------------|
| Zero/Outdated Website | +2 | No website or 90s design |
| No Active Social Media | +2 | Missing Facebook or last post > 6 months |
| Missing Industry-Specific Tool | +2 | No chat, no booking, no reviews |
| Poor Content/SEO | +1 | <3 Google reviews |
| Recent Complaint Signals | +1 | Recent negative review about responsiveness |
| No Google Business Profile | +2 | Not found on Google Maps |

## ⚙️ Configuration

**config.yaml** controls verticals, markets, and thresholds:

```yaml
verticals:
  - name: "Auto Repair"
    keywords: ["auto repair", "mechanic", "brake shop"]
  - name: "Chiropractic"
    keywords: ["chiropractor", "back pain", "spinal"]
  - name: "Real Estate"
    keywords: ["realtor", "real estate agent", "home sales"]

markets:
  - "Las Vegas, NV"
  - "Henderson, NV"

gap_scoring:
  hot_min: 8     # Auto-route to scoring engine
  warm_min: 5
```

## 📊 Opportunity Pipeline

```
Tony's Italian → No SSL + No Chat → 10/10 HOT
  → CALL_THIS_WEEK → Webhook → GHL + Client alert

Desert Auto → No Google Profile + No Reviews → 4/10 COLD
  → RECON_6_MOS → Nurture for later
```

## 🔗 Downstream Integration

HOT/WARM opportunities POST to Hermes scoring engine:
```
POST http://127.0.0.1:5000/webhook/nex-trends-router
```

See [`LexPorrello/hermes-scoring-engines`](https://github.com/LexPorrello/hermes-scoring-engines) for scoring engine details.

## 📈 Stats

- **~349 LOC** — lightweight but extensible
- **6 gap detectors** (website, social, tools, SEO, complaint, GMB)
- **Per-vertical profiles** with customizable keywords
- **Stub mode** — works without API keys

## 🛡️ License

Nex-Trends Partnership — Lex retains code ownership.

---

Built for [Nex-Trends](https://github.com/LexPorrello) | Air & Water Systems Company
