import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config

class PitchGenerator:
    """Service for generating personalized pitches with AI and fallback templates"""
    
    def __init__(self, api_key=None, user_skill='Web Development', user_name='', tone='professional'):
        self.api_key = api_key
        self.user_skill = user_skill
        self.user_name = user_name or 'Your Name'
        self.tone = tone
        self.base_url = 'https://api.cerebras.ai/v1/chat/completions'
    
    def create_session_with_retries(self):
        """Create requests session with retry logic"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # Wait 1s, 2s, 4s between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session
    
    def get_system_prompt(self):
        """Generate system prompt based on user settings"""
        tone_map = {
            'professional': 'Professional and polished',
            'casual': 'Casual and friendly',
            'friendly': 'Warm and approachable'
        }
        
        return f"""You are a professional {self.user_skill} freelancer reaching out to local businesses.

Your goal: Write a short, personalized cold outreach message.

Rules:
1. 3-4 sentences maximum (WhatsApp-friendly)
2. Mention ONE specific detail about their business
3. Focus on THEIR benefit, not your credentials
4. End with a low-pressure question
5. Tone: {tone_map.get(self.tone, 'Professional')}
6. Do NOT use clichés like "I hope this message finds you well"
7. Be specific and genuine

Good example:
"Hi, I noticed [Business] doesn't have a website yet. With your [specific detail], a simple site could help you [specific benefit]. Would you be open to a brief conversation about this?"
"""
    
    def build_user_prompt(self, business_data):
        """Build user prompt with business details"""
        return f"""Business: {business_data.get('name', 'Unknown')}
Category: {business_data.get('category', 'Business')}
Location: {business_data.get('address', 'Kenya')}
Rating: {business_data.get('rating', 'N/A')} ({business_data.get('review_count', 0)} reviews)
Discovery: {business_data.get('discovery_analysis', 'No website detected')}
Review snippet: "{business_data.get('review_snippet', '')}"

Generate a personalized outreach message."""
    
    def generate_with_ai(self, business_data):
        """
        Generate pitch using Cerebras AI
        
        Returns:
            str: Generated pitch or None if failed
        """
        if not self.api_key:
            return None
        
        try:
            session = self.create_session_with_retries()
            
            payload = {
                'model': 'gpt-oss-120b',
                'messages': [
                    {
                        'role': 'system',
                        'content': self.get_system_prompt()
                    },
                    {
                        'role': 'user',
                        'content': self.build_user_prompt(business_data)
                    }
                ],
                'max_tokens': 200,
                'temperature': 0.7
            }
            
            response = session.post(
                self.base_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=payload,
                timeout=config.TIMEOUTS['cerebras_api']
            )
            
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.Timeout:
            print(f"Cerebras API timeout for {business_data.get('name')}")
            return None
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Cerebras rate limit hit")
            elif e.response.status_code == 401:
                print(f"Invalid Cerebras API key")
            return None
        except Exception as e:
            print(f"Cerebras API error: {e}")
            return None
    
    def generate_template_pitch(self, business_data):
        """
        Generate pitch using template (fallback when AI unavailable)
        
        Returns:
            str: Template-based pitch
        """
        templates = {
            'no_website': """Hi,

I noticed {business_name} doesn't have a website yet. I'm a {user_skill} professional who helps {category} businesses in {location} get online.

{extra_detail}

Would you be open to a brief conversation about what this could look like?

Best,
{user_name}""",
            
            'broken_website': """Hi,

I noticed {business_name}'s website appears to be having some issues. I'm a {user_skill} professional who helps {category} businesses maintain their online presence.

Would you be interested in discussing how to get your site back up and running?

Best,
{user_name}""",
            
            'default': """Hi,

I'm a {user_skill} professional who helps {category} businesses in {location} improve their online presence.

{extra_detail}

Would you be interested in a brief conversation about how I can help {business_name}?

Best,
{user_name}"""
        }
        
        # Determine which template to use
        website_status = business_data.get('website_status', 'unknown')
        if website_status == 'no_website':
            template = templates['no_website']
        elif website_status in ['broken', 'timeout']:
            template = templates['broken_website']
        else:
            template = templates['default']
        
        # Build extra detail from rating or review
        extra_detail = ""
        rating = business_data.get('rating')
        review_count = business_data.get('review_count', 0)
        
        if rating and rating >= 4.0:
            extra_detail = f"With your {rating}★ rating and {review_count} reviews, a website could help you reach even more customers."
        elif business_data.get('review_snippet'):
            snippet = business_data['review_snippet'][:80]
            extra_detail = f"I saw great customer feedback about your business, and a website could help showcase that."
        else:
            extra_detail = f"A simple, professional website could help you attract more customers and build credibility."
        
        # Format template
        pitch = template.format(
            business_name=business_data.get('name', 'your business'),
            user_skill=self.user_skill.lower(),
            category=business_data.get('category', 'local').lower() if business_data.get('category') else 'local',
            location=business_data.get('address', 'Kenya').split(',')[0] if business_data.get('address') else 'your area',
            extra_detail=extra_detail,
            rating=rating or 'N/A',
            review_count=review_count,
            user_name=self.user_name
        )
        
        return pitch.strip()
    
    def generate_pitch(self, business_data):
        """
        Generate pitch with AI, fallback to template if AI fails
        
        Returns:
            tuple: (pitch_text, source)
            source is 'ai' or 'template'
        """
        # Try AI first if API key available
        if self.api_key:
            ai_pitch = self.generate_with_ai(business_data)
            if ai_pitch:
                return ai_pitch, 'ai'
        
        # Fallback to template
        template_pitch = self.generate_template_pitch(business_data)
        return template_pitch, 'template'
    
    def generate_batch(self, businesses_data):
        """
        Generate pitches for multiple businesses
        
        Returns:
            list: Results with pitch and source for each business
        """
        results = []
        
        for business in businesses_data:
            pitch, source = self.generate_pitch(business)
            
            results.append({
                'business_id': business.get('id'),
                'name': business.get('name'),
                'pitch': pitch,
                'source': source,
                'status': 'success'
            })
        
        return results
