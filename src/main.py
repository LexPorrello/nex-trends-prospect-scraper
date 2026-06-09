"""Main CLI for Nex-Trends Prospect Scraper."""
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

from detectors.gap_detector import GapDetector

load_dotenv()

def load_config() -> dict:
    """Load configuration from config.yaml."""
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path) as f:
        return yaml.safe_load(f)

def cmd_discover():
    """Run discovery across all target industries."""
    print("🚀 Starting Nex-Trends Prospect Discovery...")
    
    config = load_config()
    detector = GapDetector(config)
    
    # Get stub businesses for testing
    stub_businesses = get_stub_businesses()
    
    print(f"📊 Analyzing {len(stub_businesses)} businesses for service gaps...\n")
    
    analyzed = []
    for business in stub_businesses:
        print(f"🔍 Analyzing: {business['business_name']}")
        enriched = detector.detect_all_gaps(business)
        analyzed.append(enriched)
        
        # Print summary
        print(f"   Gaps: {len(enriched['gaps'])} detected")
        print(f"   Score: {enriched['gap_score']}/10")
        print(f"   Tier: {enriched['opportunity_tier'].upper()}")
        if enriched['gaps']:
            print(f"   Issues: {', '.join(enriched['gaps'])}")
        print()
    
    # Summary
    hot = [b for b in analyzed if b['opportunity_tier'] == 'hot']
    warm = [b for b in analyzed if b['opportunity_tier'] == 'warm']
    cold = [b for b in analyzed if b['opportunity_tier'] == 'cold']
    
    print(f"✅ Discovery complete!")
    print(f"   HOT prospects: {len(hot)}")
    print(f"   WARM prospects: {len(warm)}")
    print(f"   COLD prospects: {len(cold)}")

def cmd_analyze():
    """Analyze a single business by URL."""
    if len(sys.argv) < 3:
        print("Usage: python src/main.py analyze <website_url>")
        sys.exit(1)
    
    url = sys.argv[2]
    
    config = load_config()
    detector = GapDetector(config)
    
    business = {
        'business_name': 'Manual Analysis',
        'website': url
    }
    
    print(f"🔍 Analyzing: {url}\n")
    result = detector.detect_all_gaps(business)
    
    print(f"Gap Score: {result['gap_score']}/10")
    print(f"Opportunity Tier: {result['opportunity_tier'].upper()}")
    print(f"\nGaps Detected ({len(result['gaps'])}):")
    for gap in result['gaps']:
        print(f"  - {gap}")
    
    print(f"\nWeb Analysis:")
    for key, value in result.get('web_analysis', {}).items():
        print(f"  {key}: {value}")

def get_stub_businesses() -> List[Dict[str, Any]]:
    """Return stub business data for testing."""
    return [
        {
            'business_name': 'Desert Dental Care',
            'website': 'http://example-dental-old.com',  # HTTP, no SSL
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
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python src/main.py [command]")
        print("\nCommands:")
        print("  discover       - Run full discovery across industries")
        print("  analyze <url>  - Analyze a single business website")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'discover':
        cmd_discover()
    elif command == 'analyze':
        cmd_analyze()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
