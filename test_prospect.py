import os
import sys

# add Codebase to path to import correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "Codebase")))

from services.lead_prospector import find_restaurant_leads
from app.routers.leads import prospect_leads, prospect_and_save_leads, ProspectRequest

print("Loaded lead prospector successfully!")

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self.json_data
        
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("Mock HTTP Error")

import requests
# Mock requests.get
_original_get = requests.get

def mock_get(url, params, **kwargs):
    if "textsearch" in url:
        return MockResponse({
            "status": "OK",
            "results": [
                {
                    "place_id": "test_id_1",
                    "name": "Test Restaurant",
                    "formatted_address": "123 Main St",
                    "rating": 4.5,
                    "user_ratings_total": 15
                }
            ],
            "next_page_token": None
        })
    elif "details" in url:
        return MockResponse({
            "status": "OK",
            "result": {
                "formatted_phone_number": "555-1234",
                "website": "http://test.com"
            }
        })
    return _original_get(url, params=params, **kwargs)

requests.get = mock_get
os.environ["GOOGLE_PLACES_API_KEY"] = "mock_key"

try:
    results = find_restaurant_leads("TestCity", 1)
    print("Test Find Results:", results)
    assert len(results) == 1
    assert results[0]["pain_score"] == (5.0 - 4.5) * 10 + 50 # 55.0
    print("Lead PROSPECTOR TEST PASSED")
except Exception as e:
    print("FAILED TEST:", e)

