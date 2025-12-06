import pandas as pd
import random
import uuid
import json

# Output file path
OUTPUT_FILE = "data/clients.csv"

# Realistic Tickers
TICKERS_RISKY = ["BTC-USD", "ETH-USD", "TSLA", "NVDA", "AMD", "NFLX", "QQQ"]
TICKERS_STABLE = ["SPY", "VTI", "MSFT", "AAPL", "GOOGL", "AMZN", "JPM"]
TICKERS_SAFE = ["BND", "GLD", "KO", "JNJ"]

def generate_portfolio(risk_profile):
    portfolio = {}
    
    if risk_profile == "Aggressive":
        # Mostly risky + stable
        picks = random.sample(TICKERS_RISKY, 3) + random.sample(TICKERS_STABLE, 2)
    elif risk_profile == "Moderate":
        # Balanced mix
        picks = random.sample(TICKERS_STABLE, 3) + random.sample(TICKERS_SAFE, 1) + random.sample(TICKERS_RISKY, 1)
    else: # Conservative
        # Mostly safe + stable
        picks = random.sample(TICKERS_SAFE, 3) + random.sample(TICKERS_STABLE, 2)
        
    for ticker in picks:
        # Random allocation amount
        portfolio[ticker] = round(random.uniform(5000, 50000), 2)
        
    return json.dumps(portfolio)

def generate_clients(num_clients=10):
    clients = []
    
    for _ in range(num_clients):
        # Age affects profile often
        age = random.randint(22, 85)
        
        if age < 35:
            profile = random.choice(["Aggressive", "Moderate"])
            goal = "Wealth Accumulation"
        elif age < 55:
            profile = random.choice(["Moderate", "Aggressive", "Conservative"])
            goal = "Retirement Planning"
        else:
            profile = random.choice(["Conservative", "Moderate"])
            goal = "Capital Preservation"

        client = {
            "CustomerId": str(uuid.uuid4())[:8],
            "Surname": random.choice(["Smith", "Johnson", "Garcia", "Martinez", "Lee", "Kim", "Patel", "Singh", "Chen", "Wong", "Hargrave", "Finley"]),
            "CreditScore": random.randint(580, 850),
            "Geography": random.choice(["North America", "Europe", "Asia"]),
            "Gender": random.choice(["Male", "Female"]),
            "Age": age,
            "Tenure": random.randint(1, 20),
            "Balance": round(random.uniform(10000, 1000000), 2),
            "NumOfProducts": random.randint(1, 4),
            "HasCrCard": random.choice([0, 1]),
            "IsActiveMember": random.choice([0, 1]),
            "EstimatedSalary": round(random.uniform(30000, 250000), 2),
            "Exited": 0,
            "RiskProfile": profile,
            "FinancialGoal": goal,
            "Portfolio": generate_portfolio(profile)
        }
        clients.append(client)
    
    df = pd.DataFrame(clients)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Generated {num_clients} clients to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_clients(15)
