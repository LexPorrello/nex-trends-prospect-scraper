"""Gap Detector - Find marketing, web, and tech service gaps."""
from typing import Dict, Any, List
import httpx
from bs4 import BeautifulSoup
import re


class GapDetector:
    """Detect service gaps in business web presence and operations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get('scoring', {}).get('weights', {})
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """
        Analyze website for technical and UX gaps.
        
        Returns: {gaps: [], gap_score: int, details: {}}
        """
        gaps = []
        gap_score = 0
        details = {}
        
        try:
            # Fetch website
            response = httpx.get(url, timeout=15, follow_redirects=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # SSL Check
            if not url.startswith('https://'):
                gaps.append('no_ssl')
                gap_score += self.weights.get('website_no_ssl', 1)
                details['ssl'] = False
            else:
                details['ssl'] = True
            
            # Mobile-friendly check (viewport meta tag)
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            if not viewport:
                gaps.append('not_mobile_friendly')
                gap_score += self.weights.get('website_not_mobile', 2)
                details['mobile_friendly'] = False
            else:
                details['mobile_friendly'] = True
            
            # Chat widget detection
            chat_indicators = [
                'intercom', 'drift', 'zendesk', 'livechat',
                'tawk', 'crisp', 'olark', 'helpscout', 'chatbot'
            ]
            
            page_text = soup.get_text().lower()
            has_chat = any(indicator in page_text for indicator in chat_indicators)
            
            if not has_chat:
                gaps.append('no_chat_widget')
                gap_score += self.weights.get('no_chat_widget', 1)
                details['has_chat'] = False
            else:
                details['has_chat'] = True
            
            # Outdated design indicators
            outdated_indicators = [
                'flash', 'marquee', 'frameset', 'blink',
                'font[color]', 'font[size]'
            ]
            
            html_str = str(soup)
            is_outdated = any(indicator in html_str.lower() for indicator in outdated_indicators)
            
            # Also check for very old copyright years
            copyright_pattern = r'©\s*(\d{4})'
            matches = re.findall(copyright_pattern, page_text)
            if matches:
                years = [int(year) for year in matches]
                oldest_year = min(years)
                if oldest_year < 2019:  # 5+ years old
                    is_outdated = True
            
            if is_outdated:
                gaps.append('outdated_design')
                gap_score += self.weights.get('website_outdated', 2)
                details['outdated'] = True
            else:
                details['outdated'] = False
            
            details['status'] = 'analyzed'
        
        except Exception as e:
            details['status'] = 'error'
            details['error'] = str(e)
            print(f"⚠️  Website analysis failed for {url}: {e}")
        
        return {
            'gaps': gaps,
            'gap_score': gap_score,
            'details': details
        }
    
    def analyze_social_presence(self, business_name: str, website: str = None) -> Dict[str, Any]:
        """
        Check for social media presence (stub implementation).
        
        In production, this would:
        1. Search for Facebook/Instagram pages
        2. Check last post date
        3. Analyze engagement metrics
        
        Returns: {gaps: [], gap_score: int, details: {}}
        """
        gaps = []
        gap_score = 0
        details = {
            'facebook': None,
            'instagram': None,
            'twitter': None
        }
        
        # STUB: In production, integrate with social APIs
        # For now, check if website has social links
        if website:
            try:
                response = httpx.get(website, timeout=15, follow_redirects=True)
                soup = BeautifulSoup(response.content, 'html.parser')
                page_html = str(soup).lower()
                
                # Check for social media links
                has_facebook = 'facebook.com' in page_html
                has_instagram = 'instagram.com' in page_html
                has_twitter = 'twitter.com' in page_html or 'x.com' in page_html
                
                details['facebook'] = 'linked' if has_facebook else None
                details['instagram'] = 'linked' if has_instagram else None
                details['twitter'] = 'linked' if has_twitter else None
                
                if not (has_facebook or has_instagram or has_twitter):
                    gaps.append('no_social_presence')
                    gap_score += self.weights.get('no_social_presence', 2)
            
            except Exception as e:
                print(f"⚠️  Social presence check failed for {website}: {e}")
        
        return {
            'gaps': gaps,
            'gap_score': gap_score,
            'details': details
        }
    
    def analyze_online_reputation(self, business_name: str) -> Dict[str, Any]:
        """
        Check online reviews (stub implementation).
        
        In production, this would query Google My Business API, Yelp API.
        
        Returns: {gaps: [], gap_score: int, details: {}}
        """
        gaps = []
        gap_score = 0
        details = {
            'google_reviews': None,
            'yelp_reviews': None
        }
        
        # STUB: Would integrate with review APIs
        # For now, always flag as gap for demo
        gaps.append('no_online_reviews')
        gap_score += self.weights.get('no_online_reviews', 1)
        
        return {
            'gaps': gaps,
            'gap_score': gap_score,
            'details': details
        }
    
    def detect_all_gaps(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all gap detection methods on a business.
        
        Returns: Enriched business dict with gap analysis
        """
        all_gaps = []
        total_gap_score = 0
        
        website = business.get('website')
        business_name = business.get('company_name', business.get('business_name'))
        
        # Website analysis
        if website:
            web_analysis = self.analyze_website(website)
            all_gaps.extend(web_analysis['gaps'])
            total_gap_score += web_analysis['gap_score']
            business['web_analysis'] = web_analysis['details']
        
        # Social presence
        social_analysis = self.analyze_social_presence(business_name, website)
        all_gaps.extend(social_analysis['gaps'])
        total_gap_score += social_analysis['gap_score']
        business['social_analysis'] = social_analysis['details']
        
        # Online reputation
        reputation_analysis = self.analyze_online_reputation(business_name)
        all_gaps.extend(reputation_analysis['gaps'])
        total_gap_score += reputation_analysis['gap_score']
        business['reputation_analysis'] = reputation_analysis['details']
        
        business['gaps'] = all_gaps
        business['gap_score'] = min(total_gap_score, 10)  # Cap at 10
        business['opportunity_tier'] = self._classify_tier(total_gap_score)
        
        return business
    
    def _classify_tier(self, score: int) -> str:
        """Classify opportunity tier based on gap score."""
        tiers = self.config.get('scoring', {}).get('tiers', {})
        
        if score >= tiers.get('hot', 7):
            return 'hot'
        elif score >= tiers.get('warm', 4):
            return 'warm'
        else:
            return 'cold'
