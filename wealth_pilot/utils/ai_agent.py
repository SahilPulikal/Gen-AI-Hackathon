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
    1. Analyze risk alignment (Client Age/Profile vs Portfolio).
    2. Identify 1 key opportunity and 1 key risk.
    3. Provide 3 short bullet points for "Action Plan".
    
    **Output Format:**
    Return a concise summary (max 150 words). Use emojis.
    *   **Risk Status:** [Aligned/Misaligned] - [One sentence reasoning]
    *   **Key Insight:** [One sentence]
    *   **Actions:**
        *   [Action 1]
        *   [Action 2]
        *   [Action 3]
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

def analyze_news_impact(news_items, portfolio, api_key=None):
    """
    Analyzes news headlines to determine impact on the client's portfolio.
    """
    if api_key:
        genai.configure(api_key=api_key)
        
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are a Financial News Analyst.
    
    **Client Portfolio:**
    {json.dumps(portfolio, indent=2)}
    
    **Recent Market News:**
    {json.dumps(news_items, indent=2)}
    
    **Task:**
    1. Identify which news items are relevant to the portfolio holdings.
    2. Classify the sentiment of each relevant news item as POSITIVE, NEGATIVE, or NEUTRAL.
    3. Provide a one-sentence "Impact Summary" for the wealth manager.
    
    **Output Format:**
    Markdown table with columns: Ticker | News Title | Sentiment | Impact Summary
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error analyzing news: {e}"

def generate_meeting_agenda(client_profile, api_key=None):
    """
    Generates a meeting agenda and script for the wealth manager.
    """
    if api_key:
        genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert Wealth Manager preparing for a client meeting.
    
    **Client Profile:**
    {json.dumps(client_profile, indent=2)}
    
    **Task:**
    Create a structured meeting agenda and a "Call Script".
    
    **Agenda Structure:**
    1. **Ice Breaker**: Personalized based on age/interests (infer from profile).
    2. **Portfolio Review**: High-level performance summary.
    3. **Goal Check-in**: Specific discussion points for their goal ({client_profile.get('FinancialGoal')}).
    4. **Action Items**: 2-3 proposed changes or products to discuss.
    
    **Tone:** Professional, empathetic, and proactive.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating agenda: {e}"

def run_scenario_simulation(portfolio, scenario, client_profile, api_key=None):
    """
    Simulates a market scenario and generates a rescue plan.
    Returns a Markdown string with Impact Analysis and Actionable Plan.
    """
    if api_key:
        genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an expert Risk Manager and Agentic AI for a Wealth Management firm.
    
    CLIENT PROFILE:
    {json.dumps(client_profile, indent=2)}
    
    CURRENT PORTFOLIO:
    {json.dumps(portfolio, indent=2)}
    
    SCENARIO TO SIMULATE:
    "{scenario}"
    
    YOUR TASK:
    1. **Impact Calculation:** Estimate the percentage drop/gain for EACH holding based on the scenario. Calculate the total projected loss in Dollars ($).
    2. **Rescue Plan:** Propose specific, actionable trades to mitigate this risk immediately.
    
    OUTPUT FORMAT (Markdown):
    ## 📉 Scenario Impact Analysis
    **Scenario:** "{scenario}"
    
    **Projected Portfolio Impact:**
    *   **Total Projected Loss:** $[Amount]
    *   **New Portfolio Value:** $[Amount]
    *   **Risk Score Change:** [Old] -> [New]
    
    ### Holding-Level Impact
    | Ticker | Current Value | Est. Change (%) | Est. New Value |
    | :--- | :--- | :--- | :--- |
    | [Ticker] | $[Value] | [+/- %] | $[Value] |
    ...
    
    ## 🛡️ "Rescue Plan" Recommendations
    *Actionable trades to protect the client.*
    
    *   **[ACTION: SELL/BUY]** [Ticker] - [Amount/Percentage]
        *   *Reasoning:* [Why?]
    *   ...
    
    ## 📧 Draft Client Communication
    *Subject: Protection Strategy regarding [Scenario]*
    
    "Dear {client_profile.get('Surname')}, given the potential for [Scenario], I've analyzed your portfolio. We project a potential impact of [Loss Amount]. However, I have a proactive plan to reduce this risk..."
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error running simulation: {e}"
