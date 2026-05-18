import json
import os
from groq import AsyncGroq # We use Async to play nicely with FastAPI WebSockets

# Initialize the client. Make sure GROQ_API_KEY is set in your environment variables.
# For Together AI or Runpod, you'd use the openai AsyncClient and point it to their base_url.
client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

async def process_with_llm(user_input: str) -> dict:
    # 1. The System Prompt (The most important part)
    # This dictates EXACTLY how the agent should behave and structure the data.
    system_prompt = """
    You are a high-speed, invisible data extraction agent operating in a real-time system.
    Your objective is to analyze the user's raw input and extract structured, actionable context.
    
    You MUST respond ONLY with a valid JSON object. Do not include markdown tags like ```json.
    
    Expected JSON schema:
    {
        "intent": "Categorize the input (e.g., 'technical_query', 'casual_chat', 'feature_request', 'bug_report')",
        "entities": {
            "technologies": ["List any specific frameworks, languages, or models mentioned (e.g., 'FastAPI', 'Qwen')"],
            "urgency_level": "High, Medium, or Low"
        },
        "summary": "A concise 3-to-5 word summary of the input."
    }
    """

    try:
        # 2. Make the Async API Call
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192", # Using Llama 3 8B for extreme speed
            
            # 3. Critical Configuration Parameters
            temperature=0.1, # Keep it low (0.0 - 0.2) so the model focuses on extraction, not creativity.
            response_format={"type": "json_object"}, # Forces the model to output strict JSON
        )
        
        # 4. Extract and Parse the Response
        raw_json_string = response.choices[0].message.content
        
        # Convert the string returned by the LLM into a Python dictionary
        structured_data = json.loads(raw_json_string)
        
        # Attach the original input just in case we need it later
        structured_data["raw_input"] = user_input
        
        return structured_data

    except json.JSONDecodeError:
        # Handle cases where the LLM hallucinates and doesn't return perfect JSON
        print("Agent failed to return valid JSON.")
        return {"raw_input": user_input, "error": "JSON parse failure", "status": "failed"}
        
    except Exception as e:
        # Handle API timeouts, rate limits, etc.
        print(f"LLM API Error: {e}")
        return {"raw_input": user_input, "error": str(e), "status": "failed"}