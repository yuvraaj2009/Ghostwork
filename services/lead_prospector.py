import os
import requests
import time
import re

def extract_email_from_website(website_url: str) -> str | None:
    if not website_url:
        return None
    try:
        # Add a realistic User-Agent so we don't get blocked
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(website_url, timeout=5, headers=headers)
        response.raise_for_status()
        html = response.text
        
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(pattern, html)
        
        junk_prefixes = ('noreply@', 'admin@', 'support@', 'webmaster@')
        
        for email in emails:
            email_lower = email.lower()
            if not email_lower.startswith(junk_prefixes):
                # We return the first valid email found
                return email_lower
                
        return None
    except Exception:
        return None

def find_restaurant_leads(city: str, min_results: int = 20) -> list:
    api_key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_PLACES_API_KEY environment variable is not set")

    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    query = f"restaurants in {city}"
    params = {
        "query": query,
        "key": api_key
    }
    
    leads = []
    
    while len(leads) < min_results:
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise RuntimeError(f"Error fetching places from Google API: {str(e)}")
            
        if data.get("status") not in ["OK", "ZERO_RESULTS"]:
            raise RuntimeError(f"Google Places API error: {data.get('status')} - {data.get('error_message', '')}")
            
        places = data.get("results", [])
        if not places:
            break
            
        for place in places:
            if len(leads) >= min_results:
                break
                
            place_id = place.get("place_id")
            
            # Fetch details for phone and website
            detail_params = {
                "place_id": place_id,
                "fields": "formatted_phone_number,website",
                "key": api_key
            }
            phone = ""
            website = ""
            
            try:
                detail_response = requests.get(details_url, params=detail_params)
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    if detail_data.get("status") == "OK":
                        detail_result = detail_data.get("result", {})
                        phone = detail_result.get("formatted_phone_number", "")
                        website = detail_result.get("website", "")
            except Exception:
                # If details fail, we just pass without phone/website
                pass
                
            # Parse rating and reviews (fallback to 0)
            rating = place.get("rating", 0.0)
            try:
                rating = float(rating)
            except (ValueError, TypeError):
                rating = 0.0
                
            total_reviews = place.get("user_ratings_total", 0)
            try:
                total_reviews = int(total_reviews)
            except (ValueError, TypeError):
                total_reviews = 0
            
            # Score each lead: pain_score = (5 - rating) * 10 + (50 if total_reviews < 20 else 0) + (30 if no website else 0)
            pain_score = (5.0 - rating) * 10.0
            if total_reviews < 20:
                pain_score += 50.0
            if not website:
                pain_score += 30.0
                
            email_found = None
            if website:
                email_found = extract_email_from_website(website)
                
            leads.append({
                "name": place.get("name", ""),
                "address": place.get("formatted_address", ""),
                "rating": rating,
                "total_reviews": total_reviews,
                "phone": phone,
                "website": website,
                "email": email_found,
                "place_id": place_id,
                "pain_score": pain_score
            })
            
        next_page_token = data.get("next_page_token")
        if not next_page_token or len(leads) >= min_results:
            break
            
        params["pagetoken"] = next_page_token
        # Google API requires a short delay before next_page_token becomes valid
        time.sleep(2)
        
    leads.sort(key=lambda x: x["pain_score"], reverse=True)
    return leads
