import pandas as pd
import numpy as np
import random
from faker import Faker
import json
import os

fake = Faker()

def generate_base_data(num_clients=50):
    """
    Generates base demographic and banking data similar to Kaggle 'Bank Churn' dataset.
    """
    data = []
    for _ in range(num_clients):
        client = {
            "CustomerId": fake.uuid4(),
            "Surname": fake.last_name(),
            "CreditScore": random.randint(350, 850),
            "Geography": random.choice(["France", "Spain", "Germany", "USA", "UK"]),
            "Gender": random.choice(["Male", "Female"]),
            "Age": random.randint(18, 90),
            "Tenure": random.randint(0, 10),
            "Balance": round(random.uniform(0, 250000), 2),
            "NumOfProducts": random.randint(1, 4),
            "HasCrCard": random.choice([0, 1]),
            "IsActiveMember": random.choice([0, 1]),
            "EstimatedSalary": round(random.uniform(20000, 200000), 2),
            "Exited": 0  # Assuming active clients for wealth management
        }
        data.append(client)
    return pd.DataFrame(data)

def generate_portfolio(balance, risk_profile):
    """
    Generates a synthetic portfolio based on balance and risk profile.
    """
    # Tickers mapping
    tickers = {
        "Conservative": ["BND", "VTI", "GLD", "KO", "JNJ"],
        "Balanced": ["VTI", "BND", "AAPL", "MSFT", "JPM"],
        "Aggressive": ["QQQ", "NVDA", "TSLA", "AMZN", "BTC-USD"]
    }
    
    selected_tickers = tickers.get(risk_profile, tickers["Balanced"])
    portfolio = {}
    
    # Allocate balance
    remaining_balance = balance
    if balance < 1000:
        return {} # Too small to invest significantly
        
    for ticker in selected_tickers[:-1]:
        allocation = random.uniform(0.1, 0.3) * balance
        portfolio[ticker] = round(allocation, 2)
        remaining_balance -= allocation
    
    # Put rest in last ticker
    portfolio[selected_tickers[-1]] = round(max(0, remaining_balance), 2)
    
    return portfolio

def enrich_data(df):
    """
    Adds Wealth Management specific fields: RiskProfile, Portfolio, Goals.
    """
    risk_profiles = []
    portfolios = []
    goals = []
    
    for _, row in df.iterrows():
        # Determine risk profile based on age and basic logic (simplistic)
        if row['Age'] > 60:
            rp = random.choice(["Conservative", "Balanced"])
        elif row['Age'] < 35:
            rp = random.choice(["Aggressive", "Balanced"])
        else:
            rp = random.choice(["Conservative", "Balanced", "Aggressive"])
        
        risk_profiles.append(rp)
        portfolios.append(json.dumps(generate_portfolio(row['Balance'], rp)))
        
        # Random Goal
        goal = random.choice(["Retirement", "Home Purchase", "Wealth Accumulation", "Education Fund", "Travel"])
        goals.append(goal)
        
    df['RiskProfile'] = risk_profiles
    df['Portfolio'] = portfolios
    df['FinancialGoal'] = goals
    
    return df

if __name__ == "__main__":
    print("Generating synthetic data...")
    df_base = generate_base_data(100)
    df_enriched = enrich_data(df_base)
    
    os.makedirs("data", exist_ok=True)
    df_enriched.to_csv("data/clients.csv", index=False)
    print(f"Data generated and saved to data/clients.csv with {len(df_enriched)} records.")
