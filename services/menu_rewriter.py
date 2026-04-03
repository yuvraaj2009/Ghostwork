import os
import google.generativeai as genai
from typing import List, Dict, Any

def rewrite_menu_descriptions(restaurant_name: str, restaurant_type: str, menu_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    genai.configure(api_key=api_key)
    # Using Gemini 2.0 Flash as it is fast and recommended for text generation
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    results = []
    
    for item in menu_items:
        dish_name = item.get("dish_name", "Unknown Dish")
        current_desc = item.get("current_description", "")
        price = item.get("price", "N/A")
        
        prompt = (
            f"You are an expert food copywriter. The restaurant '{restaurant_name}' is a '{restaurant_type}'. "
            f"Rewrite the description for the dish '{dish_name}'.\n"
            f"Original Description: {current_desc}\n\n"
            f"Make the new description appetizing, sensory-rich, and keep it under 40 words. "
            f"Return ONLY the new description text."
        )
        
        try:
            response = model.generate_content(prompt)
            new_description = response.text.strip()
        except Exception as e:
            new_description = f"Error generating description: {str(e)}"
            
        results.append({
            "dish_name": dish_name,
            "original_description": current_desc,
            "new_description": new_description,
            "price": price
        })
        
    return results
