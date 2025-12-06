# WealthPilot - Hackathon Submission

## 1. Business Challenge / Problem Statement
**The Challenge:** Wealth Managers today are overwhelmed with data. They manage hundreds of clients, each with unique portfolios, goals, and risk profiles. Simultaneously, they must track thousands of market news events daily.
**The Gap:** Existing tools are passive. They show data but don't interpret it. Wealth managers spend hours manually connecting the dots between "Market News" and "Client Impact," leading to missed opportunities and reactive (rather than proactive) client service.
**The Goal:** To build an "Agentic AI" workspace that proactively monitors the market, understands client context, and drafts actionable insights automatically.

## 2. Solution and Architecture
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

## 3. Prompts Used for the Solution
**Portfolio Analysis Agent:**
> "You are an expert Wealth Management AI Assistant. Analyze the client's portfolio risk alignment with their profile (Age, Risk Profile). Identify any concentration risks or opportunities based on the market context. Provide 3 actionable recommendations."

**News Impact Agent:**
> "You are a Financial News Analyst. Identify which news items are relevant to the portfolio holdings. Classify the sentiment of each relevant news item as POSITIVE, NEGATIVE, or NEUTRAL. Provide a one-sentence 'Impact Summary' for the wealth manager."

**Meeting Prep Agent:**
> "You are an expert Wealth Manager preparing for a client meeting. Create a structured meeting agenda and a 'Call Script'. Include: Ice Breaker (personalized), Portfolio Review, Goal Check-in, and Action Items. Tone: Professional, empathetic, and proactive."

## 4. Tech Stack Used
*   **Programming Language:** Python 3.9+
*   **Frontend Framework:** Streamlit
*   **Data Manipulation:** Pandas, NumPy
*   **Visualization:** Plotly Express

## 5. APIs Used
*   **Google Gemini API (`google-generativeai`):** For all reasoning, analysis, and content generation tasks.
*   **Yahoo Finance API (`yfinance`):** For fetching real-time stock prices, historical data, and market news.

## 6. Tools Used
*   **VS Code:** For development.
*   **Google AI Studio:** For prompt engineering and testing.
*   **Git/GitHub:** For version control.
