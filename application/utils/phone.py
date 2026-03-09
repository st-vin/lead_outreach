import re
import phonenumbers
from phonenumbers import NumberParseException
from urllib.parse import quote_plus

def is_phone_like(value):
    """
    Quick heuristic check if value looks like a phone number
    
    Args:
        value: String or number to check
    
    Returns:
        bool: True if value looks phone-like
    """
    if not value:
        return False
    
    # Extract only digits
    digits = ''.join(filter(str.isdigit, str(value)))
    
    # International phone numbers are typically 9-15 digits
    return 9 <= len(digits) <= 15

def normalize_phone(phone, country_code='+254', region='KE'):
    """
    Normalize phone number to international format
    
    Args:
        phone: Raw phone number string
        country_code: Default country code (e.g., '+254' for Kenya)
        region: Country region code (e.g., 'KE' for Kenya)
    
    Returns:
        Normalized phone number in E164 format or None if invalid
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    clean = re.sub(r'[^\d+]', '', str(phone))
    
    # Quick check if it looks phone-like
    if not is_phone_like(clean):
        return None
    
    # If already starts with country code, use as is
    if clean.startswith(country_code.replace('+', '')):
        normalized = f"+{clean}" if not clean.startswith('+') else clean
    elif clean.startswith('+'):
        normalized = clean
    else:
        # Remove leading zero (common in Kenya: 0712345678 -> 712345678)
        if clean.startswith('0'):
            clean = clean[1:]
        
        # Add country code
        normalized = f"{country_code}{clean}"
    
    # Validate using phonenumbers library
    try:
        parsed = phonenumbers.parse(normalized, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
    except (NumberParseException, Exception):
        pass
    
    # If validation fails but format looks reasonable, return it anyway
    if len(clean) >= 9:
        return normalized
    
    return None

def create_whatsapp_link(phone, message=''):
    """
    Create WhatsApp link with pre-filled message
    
    Args:
        phone: Normalized phone number (with country code)
        message: Pre-filled message text
    
    Returns:
        WhatsApp URL or None if phone invalid
    """
    if not phone:
        return None
    
    # Remove + and spaces from phone (expects E.164 like +2547...)
    clean_phone = phone.replace('+', '').replace(' ', '')
    
    # URL encode the message in a WhatsApp-friendly way (spaces -> +)
    encoded_message = quote_plus(message) if message else ''
    
    # Build full WhatsApp "click to chat" URL
    base_url = "https://api.whatsapp.com/send/"
    url = f"{base_url}?phone={clean_phone}"
    
    if encoded_message:
        url += f"&text={encoded_message}"
    
    # Align with WhatsApp's phone link format
    url += "&type=phone_number&app_absent=0"
    
    return url

def validate_business_phone(phone_raw, country_code='+254'):
    """
    Validate and normalize business phone number
    
    Args:
        phone_raw: Raw phone number from CSV
        country_code: Country code for normalization
    
    Returns:
        dict with 'normalized' (phone or None) and 'reason' (if invalid)
    """
    if not phone_raw or str(phone_raw).strip() == '':
        return {
            'normalized': None,
            'reason': 'Missing phone number'
        }
    
    normalized = normalize_phone(phone_raw, country_code)
    
    if not normalized:
        return {
            'normalized': None,
            'reason': f'Invalid phone format: {phone_raw}'
        }
    
    return {
        'normalized': normalized,
        'reason': None
    }
