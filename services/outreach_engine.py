import os
import json
import requests
import google.generativeai as genai
from typing import Dict, Any, List

def generate_email_content(lead_data: Dict[str, Any], template_type: str = "review_help") -> Dict[str, str]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    # Using Gemini 2.0 Flash for personalization
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    restaurant_name = lead_data.get("business_name", "your restaurant")
    city = lead_data.get("city", "your city")
    
    if template_type == "review_help":
        rating = lead_data.get("google_rating", 0.0)
        review_count = lead_data.get("review_count", 0)
        prompt = (
            f"You are the founder of GhostWork, an AI automation agency for restaurants. "
            f"Write a short, compelling cold email to the owner of {restaurant_name} located in {city}. "
            f"The focus of the email must be: 'I wrote 5 free review responses for your restaurant. Want to see them?' "
            f"Mention their specific rating ({rating} stars) and their number of reviews ({review_count}). "
            f"Keep it under 100 words. Do not include placeholders like [Your Name] or [Insert Link]. Sign off as 'GhostWork AI Services'. "
            f"The tone should be friendly, helpful, and concise. "
            f"Format the output strictly as a JSON object with two keys: 'subject' (exactly: I wrote 5 free review responses for {restaurant_name}) and 'body_html' (the email body formatted with basic HTML tags like <p> and <br>)."
        )
    else:
        prompt = (
            f"You are the founder of GhostWork. Write a short check-in email to the owner of {restaurant_name}. "
            f"Keep it under 100 words. Sign off as 'Alex from GhostWork'. "
            f"Format the output strictly as a JSON object with two keys: 'subject' and 'body_html'."
        )

    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return {
            "subject": f"Quick question regarding {restaurant_name}",
            "body_html": f"<p>Hello,</p><p>I've noticed {restaurant_name} and wanted to reach out. We built some AI tools that might help augment your workflow.</p><p>Alex from GhostWork</p>"
        }

def send_outreach_email(lead_data: Dict[str, Any], template_type: str = "review_help") -> Dict[str, Any]:
    resend_api_key = os.environ.get("RESEND_API_KEY")
    sender_email = os.environ.get("SENDER_EMAIL")
    
    if not resend_api_key:
        raise ValueError("RESEND_API_KEY environment variable is not set")
    if not sender_email:
        raise ValueError("SENDER_EMAIL environment variable is not set")

    email_contact = lead_data.get("contact_email")
    if not email_contact:
        return {"success": False, "error": "no email available"}

    # Generate content using Gemini
    try:
        content = generate_email_content(lead_data, template_type)
    except Exception as e:
        return {"success": False, "error": f"Failed to generate email content: {str(e)}"}
        
    headers = {
        "Authorization": f"Bearer {resend_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": sender_email,
        "to": [email_contact],
        "subject": content.get("subject", "Hello from GhostWork"),
        "html": content.get("body_html", "<p>Hello from GhostWork!</p>")
    }
    
    try:
        response = requests.post("https://api.resend.com/emails", headers=headers, json=payload, timeout=10)
        if response.status_code in [200, 201]:
            return {"success": True, "resend_id": response.json().get("id", ""), "detail": "Email sent"}
        else:
            return {"success": False, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def send_batch_outreach(leads_list: List[Dict[str, Any]], db, template_type: str = "review_help", daily_limit: int = 10):
    from app.models import OutreachLog
    
    results = []
    leads_to_process = leads_list[:daily_limit]
    
    for lead in leads_to_process:
        result = send_outreach_email(lead, template_type)
        
        # Log to db only if it didn't skip due to no email
        if not result.get("success") and result.get("error") == "no email available":
            # Just record failure logic
            pass
            
        lead_id = lead.get("id")
        if lead_id:
            status = "sent" if result["success"] else "failed"
            log_entry = OutreachLog(
                lead_id=lead_id,
                template_id=template_type,
                channel="email",
                status=status
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            
            result["log_id"] = log_entry.id
            
        results.append({"lead_id": lead_id, "result": result})
        
    return results
