import os
import json
import google.generativeai as genai
from typing import Dict, List, Any

def generate_social_media_pack(
    restaurant_name: str, 
    restaurant_type: str, 
    cuisine: str, 
    location: str, 
    tone: str, 
    days: int = 30
) -> List[Dict[str, Any]]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
        
    genai.configure(api_key=api_key)
    # Using Gemini 2.0 Flash as it is fast and recommended for most text generation tasks
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = (
        f"You are an expert social media manager for {restaurant_name}, a {restaurant_type} "
        f"serving {cuisine} cuisine in {location}. Your brand tone is {tone}.\n\n"
        f"Create a {days}-day social media content calendar.\n"
        "Requirements:\n"
        "- For each day, provide: 'day_number' (integer), 'post_text' (string), 'suggested_hashtags' (list of strings), and 'post_type' (string: one of 'image_idea', 'reel_idea', 'story_idea', 'text_post').\n"
        "- Mix content themes approximately as follows: 40% food highlights, 20% behind-the-scenes, 15% customer stories, 15% offers/promos, 10% fun/engagement.\n"
        "- Emphasize visually appealing post types where appropriate.\n"
        "- Keep each post_text under 150 words.\n\n"
        "Return the output as a valid JSON array of objects representing each day."
    )
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        
        content = json.loads(response.text)
        if isinstance(content, list):
            return content
        elif isinstance(content, dict):
            # Try to handle if model returns an object with a list inside
            for k, v in content.items():
                if isinstance(v, list):
                    return v
            return [content]
        else:
            return [{"error": "Unexpected JSON structure returned from model"}]
            
    except Exception as e:
        return [{"error": f"Failed to generate social media pack: {str(e)}"}]
