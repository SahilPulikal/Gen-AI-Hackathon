# WealthPilot - Wealth Manager Enablement Tool

## Overview
WealthPilot is an Agentic AI application designed to help wealth managers proactively manage client portfolios. It combines real-time market data with client profiles to generate actionable insights.

## Features
- **Dashboard**: High-level view of all clients with risk alerts and demographics.
- **Client 360**: Detailed view of client portfolios with enriched metadata (Ticker Names, Asset Categories).
- **Proactive AI Agent**: Chat with your data to ask specific questions.
- **Scenario Simulator ("Black Swan")**: Simulate market shocks (e.g., "Tech Crash 20%") and get an instant portfolio impact assessment.
- **Strategy Crew (Multi-Agent)**: A dedicated team of AI agents (Market Analyst, Risk Manager, Wealth Manager) that collaboratively analyzes the portfolio and suggests opportunities.
- **Real-Time Feedback**: Live status updates showing exactly which AI agent is working on your request.
- **Market Intelligence**: Real-time tracking of key indices and individual stock histories.
- **Report Generation**: Export comprehensive client summaries to PDF.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Data**:
   ```bash
   python utils/data_generator.py
   ```
   This will create `data/clients.csv` with realistic synthetic data (diverse ages, portfolios).

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

4. **API Key**:
   - You will need a Google Gemini API Key.
   - Enter it in the sidebar when the app launches.

## Tech Stack
- **Frontend**: Streamlit (Python) with Custom CSS
- **Data**: Pandas, Faker (Synthetic), yfinance (Real Market Data)
- **AI Core**: Google Gemini 2.5 Flash (via `google-generativeai`)
- **Agent Framework**: Custom Lightweight Multi-Agent Engine (mimicking CrewAI architecture)
- **Visualization**: Plotly Express
- **Reporting**: FPDF


## Hackathon Submission Details

### 1. Business Challenge / Problem Statement
**The Challenge:** Wealth Managers today are overwhelmed with data. They manage hundreds of clients, each with unique portfolios, goals, and risk profiles. Simultaneously, they must track thousands of market news events daily.
**The Gap:** Existing tools are passive. They show data but don't interpret it. Wealth managers spend hours manually connecting the dots between "Market News" and "Client Impact," leading to missed opportunities and reactive (rather than proactive) client service.
**The Goal:** To build an "Agentic AI" workspace that proactively monitors the market, understands client context, and drafts actionable insights automatically.

### 2. Solution and Architecture
**Solution Name:** WealthPilot
**Core Concept:** A "Proactive AI Co-pilot" for Wealth Managers.
**Key Features:**
*   **Client 360° Dashboard:** Unified view of client demographics, risk profile, and live portfolio holdings.
*   **News Impact Agent:** An autonomous agent that scans real-time market news and classifies it as Positive/Negative/Neutral *specifically* for the client's holdings.
*   **Meeting Prep Agent:** One-click generation of a personalized meeting agenda and call script, synthesizing portfolio performance and client goals.
*   **Interactive Chat:** A "Talk to your Data" interface allowing managers to ask complex questions like "How does the tech sector drop affect this client?"

**Architecture:**
*   **Frontend:** Streamlit (Python) for a responsive, professional web interface.
*   **Data Layer:**
    *   **Client Data:** Synthetic high-fidelity data (Faker) mimicking real banking profiles.
    *   **Market Data:** Live stock prices and news via `yfinance` API.
*   **Intelligence Layer:**
    *   **LLM:** Google Gemini 2.5 Flash (via `google-generativeai`).
    *   **Agentic Logic:** Custom Python functions that chain data retrieval with LLM reasoning.

### 3. Prompts Used for the Solution
**Portfolio Analysis Agent:**
> "You are an expert Wealth Management AI Assistant. Analyze the client's portfolio risk alignment with their profile (Age, Risk Profile). Identify any concentration risks or opportunities based on the market context. Provide 3 actionable recommendations."

**News Impact Agent:**
> "You are a Financial News Analyst. Identify which news items are relevant to the portfolio holdings. Classify the sentiment of each relevant news item as POSITIVE, NEGATIVE, or NEUTRAL. Provide a one-sentence 'Impact Summary' for the wealth manager."

**Meeting Prep Agent:**
> "You are an expert Wealth Manager preparing for a client meeting. Create a structured meeting agenda and a 'Call Script'. Include: Ice Breaker (personalized), Portfolio Review, Goal Check-in, and Action Items. Tone: Professional, empathetic, and proactive."

### 4. Tech Stack Used
*   **Programming Language:** Python 3.9+
*   **Frontend Framework:** Streamlit
*   **Data Manipulation:** Pandas, NumPy
*   **Visualization:** Plotly Express

### 5. APIs Used
*   **Google Gemini API (`google-generativeai`):** For all reasoning, analysis, and content generation tasks.
*   **Yahoo Finance API (`yfinance`):** For fetching real-time stock prices, historical data, and market news.

### 6. Tools Used
*   **VS Code:** For development.
*   **Google AI Studio:** For prompt engineering and testing.
*   **Git/GitHub:** For version control.
