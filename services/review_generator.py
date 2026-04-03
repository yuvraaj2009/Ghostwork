import os
import google.generativeai as genai
from typing import List, Dict

def generate_review_responses(restaurant_name: str, restaurant_type: str, tone: str, reviews_list: List[str]) -> List[Dict[str, str]]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    genai.configure(api_key=api_key)
    # Using Gemini 2.0 Flash as it is fast and recommended for most text generation tasks
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    results = []
    
    for review in reviews_list:
        prompt = (
            f"You are a professional customer service representative for {restaurant_name}, a {restaurant_type}. "
            f"Respond to the following customer review in a {tone} tone. Keep the response under 100 words. "
            f"Be genuine, address specific points the customer raised, and end with an invitation to return. "
            f"Review: {review}"
        )
        try:
            response = model.generate_content(prompt)
            generated_text = response.text.strip()
        except Exception as e:
            generated_text = f"Error generating response: {str(e)}"
            
        results.append({
            "original_review": review,
            "generated_response": generated_text
        })
        
    return results
