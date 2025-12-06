from utils.crew_agent import run_crew_analysis
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("No API Key found!")
    exit()

client = {
    "Age": 45,
    "RiskProfile": "Moderate",
    "Portfolio": {"SPY": 10000, "QQQ": 5000}
}
portfolio = {"SPY": 10000, "QQQ": 5000}
market_data = "SPY: Bullish trend. QQQ: High volatility."

print("Running Crew Analysis...")
result = run_crew_analysis(client, portfolio, market_data, api_key=api_key)
print("Result Type:", type(result))
print("Result Keys:", result.keys() if isinstance(result, dict) else "Not a dict")
print("Full Result:")
print(json.dumps(result, indent=2))
