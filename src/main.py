"""Main CLI for Nex-Trends Prospect Scraper with Hermes webhook triggers."""
import sys
import yaml
import httpx
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

from detectors.gap_detector import GapDetector

# Hermes webhook URL
WEBHOOK_URL = "http://127.0.0.1:5000/webhook/nex-trends-router"
load_dotenv()

def load_config():
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path) as f:
        return yaml.safe_load(f)

def send_to_hermes(business: dict):
    """Push HOT/WARM opportunity to Hermes scoring engine."""
    try:
        payload = {
            "business_name": business['business_name'],
            "website": business.get('website', ''),
            "phone": business.get('phone', ''),
            "industry": business.get('industry', 'general'),
            "gap_score": business['gap_score'],
            "opportunity_tier": business['opportunity_tier'],
            "gaps": business.get('gaps', []),
            "has_chat_widget": business.get('has_chat_widget'),
        }
        resp = httpx.post(WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"⚠️  Webhook failed: {e}")
        return False

def cmd_discover():
    """Run discovery with Hermes webhook routing."""
    print("🚀 Nex-Trends Discovery + Hermes Scoring Engine")
    config = load_config()
    detector = GapDetector(config)
    
    businesses = get_stub_businesses()
    print(f"📊 Analyzing {len(businesses)} businesses...\n")
    
    hermes_count = 0
    
    for business in businesses:
        print(f"🔍 {business['business_name']}")
        enriched = detector.detect_all_gaps(business)
        
        # Route HOT/WARM to Hermes
        tier = enriched['opportunity_tier']
        if tier in ['hot', 'warm']:
            sent = send_to_hermes(enriched)
            if sent:
                hermes_count += 1
                action = "→ Hermes"
            else:
                action = "→ Local only"
        else:
            action = ""
        
        print(f"   Score: {enriched['gap_score']}/10 | {tier.upper()} {action}")
        if enriched['gaps']:
            print(f"   Gaps: {', '.join(enriched['gaps'])}")
        print()
    
    print(f"\n✅ Done. Hermes routed: {hermes_count}")

def cmd_analyze():
    if len(sys.argv) < 3:
        print("Usage: python src/main.py analyze <url>")
        sys.exit(1)
    
    url = sys.argv[2]
    config = load_config()
    detector = GapDetector(config)
    
    business = {'business_name': 'Manual', 'website': url}
    result = detector.detect_all_gaps(business)
    
    print(f"Score: {result['gap_score']}/10 | {result['opportunity_tier'].upper()}")
    if result['tier'] in ['hot', 'warm']:
        send_to_hermes(result)
        print("→ Routed to Hermes")

def get_stub_businesses() -> List[Dict[str, Any]]:
    return [
        {
            'business_name': 'Desert Dental Care',
            'website': 'http://example-dental-old.com',
            'phone': '(702) 555-0100',
            'industry': 'healthcare'
        },
        {
            'business_name': 'Las Vegas Auto Repair',
            'website': 'https://example-auto-repair.com',
            'phone': '(702) 555-0200',
            'industry': 'automotive'
        },
        {
            'business_name': 'Bella Salon & Spa',
            'website': 'https://example-salon.com',
            'phone': '(702) 555-0300',
            'industry': 'beauty_wellness'
        }
    ]

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py [discover|analyze <url>]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == 'discover':
        cmd_discover()
    elif cmd == 'analyze':
        cmd_analyze()
    else:
        print(f"Unknown: {cmd}")

if __name__ == '__main__':
    main()
