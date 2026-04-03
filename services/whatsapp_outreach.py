import urllib.parse
import re

def generate_whatsapp_link(phone: str, restaurant_name: str, rating: float) -> str | None:
    if not phone:
        return None
        
    # Clean phone number: remove anything that is not a digit or '+'
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # If the phone number doesn't start with '+', assume it's Indian (+91)
    if not cleaned_phone.startswith('+'):
        # Sometimes local numbers start with 0, strip it if so
        if cleaned_phone.startswith('0'):
            cleaned_phone = cleaned_phone[1:]
        cleaned_phone = '+91' + cleaned_phone
        
    # Remove the '+' for the wa.me link format (wa.me expects just numbers, e.g., 919876543210)
    cleaned_phone = cleaned_phone.replace('+', '')
    
    # Template message matching the user's hardcoded requirement
    template = (
        f"Hi! I noticed {restaurant_name} has a {rating}/5 rating on Google. "
        f"I specialize in helping restaurants improve their online reputation using AI. "
        f"I've already prepared 5 free sample review responses for your restaurant - would you like to see them? "
        f"No charge, no commitment. - Yuvraaj, GhostWork AI Services"
    )
    
    encoded_message = urllib.parse.quote(template)
    
    return f"https://wa.me/{cleaned_phone}?text={encoded_message}"
