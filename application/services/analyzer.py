import requests
from application.models import WebsiteStatus
import config

class BusinessAnalyzer:
    """Service for analyzing businesses and calculating opportunity scores"""
    
    def __init__(self, user_skill='Web Development'):
        self.user_skill = user_skill
    
    def check_website(self, website_url):
        """
        Check if website exists and is accessible (with timeout)
        
        Returns:
            tuple: (WebsiteStatus, score, message)
        """
        if not website_url:
            return (
                WebsiteStatus.NO_WEBSITE,
                100,
                "No website detected - high opportunity"
            )
        
        try:
            # Try to access the website with timeout
            response = requests.head(
                website_url, 
                timeout=config.TIMEOUTS['website_check'],
                allow_redirects=True
            )
            
            if response.status_code >= 400:
                return (
                    WebsiteStatus.BROKEN,
                    90,
                    "Website appears broken or inaccessible"
                )
            
            # Website exists and is accessible
            return (
                WebsiteStatus.HAS_WEBSITE,
                20,
                "Already has a functional website"
            )
                
        except requests.exceptions.Timeout:
            return (
                WebsiteStatus.TIMEOUT,
                85,
                "Website is too slow or unresponsive"
            )
        except requests.exceptions.ConnectionError:
            return (
                WebsiteStatus.BROKEN,
                85,
                "Website unreachable"
            )
        except Exception:
            return (
                WebsiteStatus.UNKNOWN,
                50,
                "Could not check website status"
            )
    
    def check_reputation(self, rating, review_count):
        """
        Analyze business reputation
        
        Returns:
            tuple: (score, message)
        """
        if not rating or rating == 0:
            return 30, "No rating data available"
        
        if rating < 3.5:
            return 70, f"Low rating ({rating}/5) - might need reputation management"
        
        if review_count and review_count < 5:
            return 50, f"Only {review_count} reviews - needs more social proof"
        
        if rating >= 4.0 and review_count and review_count >= 10:
            return 90, f"Strong reputation ({rating}/5 with {review_count} reviews)"
        
        return 60, f"Good reputation ({rating}/5)"
    
    def calculate_opportunity_score(self, business_data):
        """
        Calculate overall opportunity score (0-100)
        
        Args:
            business_data: dict with business information
        
        Returns:
            int: Opportunity score
        """
        score = 0
        
        # Website status is most important factor (50 points max)
        website_url = business_data.get('website_url')
        website_status, website_score, _ = self.check_website(website_url)
        score += int(website_score * 0.5)  # 50% weight
        
        # Reputation (30 points max)
        rating = business_data.get('rating')
        review_count = business_data.get('review_count', 0)
        reputation_score, _ = self.check_reputation(rating, review_count)
        score += int(reputation_score * 0.3)  # 30% weight
        
        # Has contact info (20 points max)
        if business_data.get('phone_normalized'):
            score += 20
        
        # Cap at 100
        return min(score, 100)
    
    def analyze_business(self, business_data):
        """
        Complete analysis of a business
        
        Args:
            business_data: dict with business information
        
        Returns:
            dict: Analysis results
        """
        # Website check
        website_status, website_score, website_message = self.check_website(
            business_data.get('website_url')
        )
        
        # Reputation check
        reputation_score, reputation_message = self.check_reputation(
            business_data.get('rating'),
            business_data.get('review_count', 0)
        )
        
        # Calculate overall score
        opportunity_score = self.calculate_opportunity_score(business_data)
        
        # Build discovery analysis text
        discovery_parts = []
        
        if website_status == WebsiteStatus.NO_WEBSITE:
            discovery_parts.append(f"🌐 {website_message}")
        elif website_status in [WebsiteStatus.BROKEN, WebsiteStatus.TIMEOUT]:
            discovery_parts.append(f"⚠️ {website_message}")
        
        if business_data.get('rating'):
            if business_data['rating'] >= 4.0:
                discovery_parts.append(f"⭐ {reputation_message}")
            else:
                discovery_parts.append(f"📊 {reputation_message}")
        
        if business_data.get('review_snippet'):
            snippet = business_data['review_snippet'][:100]
            discovery_parts.append(f"💬 Customer says: \"{snippet}...\"")
        
        discovery_analysis = " | ".join(discovery_parts) if discovery_parts else "Limited information available"
        
        return {
            'website_status': website_status,
            'opportunity_score': opportunity_score,
            'discovery_analysis': discovery_analysis
        }
