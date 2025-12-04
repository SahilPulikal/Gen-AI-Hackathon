import google.generativeai as genai
import os
import json

# Configure API Key
# Ideally, this should be loaded from environment variables or a config file
# For the hackathon, we can ask the user to input it in the UI or set it here.
# We will check for the env var first.

def configure_genai(api_key):
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def get_portfolio_analysis(client_profile, market_summary):
    """
    Generates a portfolio analysis using Gemini.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert Wealth Management AI Assistant.
    
    **Client Profile:**
    {json.dumps(client_profile, indent=2)}
    
    **Market Context (Key Tickers):**
    {market_summary.to_string() if hasattr(market_summary, 'to_string') else market_summary}
    
    **Task:**
    1. Analyze the client's portfolio risk alignment with their profile (Age, Risk Profile).
    2. Identify any concentration risks or opportunities based on the market context.
    3. Provide 3 actionable recommendations.
    
    **Output Format:**
    Return the response in Markdown format with clear headers.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating analysis: {e}"

def chat_with_agent(query, context):
    """
    Chat with the agent about a specific client context.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Context:
    {context}
    
    User Query: {query}
    
    Answer as a helpful Wealth Manager Assistant. Keep it concise.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error responding to chat: {e}"
