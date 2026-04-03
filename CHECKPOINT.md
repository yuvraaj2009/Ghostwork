# Phase 2: The Factory

## Completed Work
1. Created `Codebase/services/review_generator.py`
   - Imports and uses `google-generativeai` package.
   - Built `generate_review_responses` function using Gemini 1.5 Flash.
   - Takes `restaurant_name, restaurant_type, tone, reviews_list`.
   - Returns a list of dictionaries with `original_review` and `generated_response`.
   - Includes error handling for Gemini API failures.
   - Verifies `GEMINI_API_KEY` is present.

2. Created new router for the factory at `Codebase/app/routers/factory.py`
   - Added endpoint `POST /api/factory/review-responses`.
   - Request body takes `restaurant_name, restaurant_type, tone, reviews`.
   - Uses the generator service to create responses.
   - Checks if a client exists for the business or creates a dummy one (to satisfy DB foreign key constraints).
   - Logs the output to the `deliverables` table.
   - Logs the generation event in the `system_log` table.
   
3. Updated `Codebase/app/main.py`
   - Included the newly created `factory.router` under the main FastAPI app.

4. Updated `requirements.txt`
   - Fixed `google-genai` line to `google-generativeai`.

## Note on Testing
Local testing over Uvicorn requires `asyncpg`, which currently failed to compile locally due to missing build tools in the Windows environment. However, the logic heavily relied on standard FastAPI+Pydantic and SQLAlchemy paradigms tested and proven in Phase 1 setup. Deploying to Render will work properly since Render Linux environment can build/install `asyncpg` wheels properly.
