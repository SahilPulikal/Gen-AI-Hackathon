import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from utils.market_data import get_market_data, get_market_news, get_ticker_history, get_ticker_info
from utils.ai_agent import configure_genai, get_portfolio_analysis, chat_with_agent, analyze_news_impact, generate_meeting_agenda, run_scenario_simulation
from utils.crew_agent import run_crew_analysis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(page_title="WealthPilot | Accenture", layout="wide", page_icon="📈")

# Custom CSS for Accenture-like feel
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #A100FF;
        color: white;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/cd/Accenture.svg", width=150)
    st.title("WealthPilot")
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Client View", "Market Intelligence"])
    st.markdown("---")
    
    # API Key Logic
    env_api_key = os.getenv("GOOGLE_API_KEY")
    if env_api_key:
        api_key = env_api_key
        st.success("✅ API Key Loaded")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
        
    if api_key:
        configure_genai(api_key)
    else:
        st.warning("Enter API Key to enable AI features")

# Session State Initialization
if 'ai_analysis' not in st.session_state:
    st.session_state['ai_analysis'] = None
if 'news_impact' not in st.session_state:
    st.session_state['news_impact'] = None
if 'meeting_agenda' not in st.session_state:
    st.session_state['meeting_agenda'] = None

# Load Data
@st.cache_data
def load_data():
    if not os.path.exists("data/clients.csv"):
        st.error("Data not found. Please run data generation script.")
        return pd.DataFrame()
    return pd.read_csv("data/clients.csv")

df_clients = load_data()

if page == "Dashboard":
    st.title("Wealth Manager Dashboard")
    
    # Top Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clients", len(df_clients))
    with col2:
        st.metric("Total AUM", f"${df_clients['Balance'].sum():,.0f}")
    with col3:
        st.metric("Avg Risk Score", "Balanced") # Placeholder
    with col4:
        churn_risk = df_clients[df_clients['CreditScore'] < 600].shape[0]
        st.metric("High Risk Clients", churn_risk, delta_color="inverse")

    st.markdown("### Client Overview")
    
    # Filter
    filter_risk = st.multiselect("Filter by Risk Profile", df_clients['RiskProfile'].unique())
    if filter_risk:
        filtered_df = df_clients[df_clients['RiskProfile'].isin(filter_risk)]
    else:
        filtered_df = df_clients
        
    st.dataframe(filtered_df[['CustomerId', 'Surname', 'Age', 'Balance', 'RiskProfile', 'FinancialGoal']], width='stretch')
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig_risk = px.pie(df_clients, names='RiskProfile', title='Client Risk Distribution', hole=0.4)
        st.plotly_chart(fig_risk, width='stretch')
    with c2:
        fig_geo = px.bar(df_clients, x='Geography', y='Balance', title='AUM by Geography')
        st.plotly_chart(fig_geo, width='stretch')
elif page == "Client View":
    st.title("Client 360° View")
    
    # Client Selection
    client_id = st.selectbox("Select Client", df_clients['CustomerId'].astype(str) + " - " + df_clients['Surname'])
    selected_id = client_id.split(" - ")[0]
    client = df_clients[df_clients['CustomerId'] == selected_id].iloc[0]
    
    # ---------------------------------------------------------
    # 1. Quick Profile Header
    # ---------------------------------------------------------
    with st.container():
        # Custom "Card" for profile
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(f"{client['Surname']}, {client['Gender']}")
            st.caption(f"ID: {client['CustomerId']}")
            
            # Metrics with minimal spacing
            st.markdown(f"**Risk Profile:** {client['RiskProfile']}") 
            st.markdown(f"**Goal:** {client['FinancialGoal']}")
            st.markdown(f"**Credit Score:** {client['CreditScore']}")

        with col2:
            st.subheader("Portfolio Allocation")
            portfolio = json.loads(client['Portfolio'])
            
            # Enrich Data
            p_data = []
            for ticker, amount in portfolio.items():
                info = get_ticker_info(ticker)
                p_data.append({
                    "Ticker": ticker,
                    "Name": info['Name'],
                    "Category": info['Category'],
                    "Value": f"${amount:,.2f}",
                    "RawValue": amount # For sorting/charting
                })
            
            df_port = pd.DataFrame(p_data)
            
            # Display Table with new columns
            st.dataframe(
                df_port[['Ticker', 'Name', 'Category', 'Value']], 
                width='stretch', 
                hide_index=True
            )
            
            # Compact Donut Chart (Categorical or Ticker)
            fig = px.pie(df_port, values='RawValue', names='Category', hole=0.5, title="Allocation by Category")
            fig.update_layout(height=250, margin=dict(t=30, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig, width='stretch')

    st.markdown("---")

    # ---------------------------------------------------------
    # 2. AI Intelligence Hub (Boxed Design)
    # ---------------------------------------------------------
    # Use st.info or st.success as a container background
    with st.container():
        st.subheader("🤖 Portfolio Intelligence")
        
        c_btn, c_res = st.columns([1, 3])
        
        with c_btn:
            st.write("Generate a quick AI scan of the portfolio's health.")
            if st.button("Generate AI Insights", type="primary"):
                with st.spinner("Scanning market & portfolio..."):
                    tickers = list(portfolio.keys())
                    market_summary = get_market_data(tickers).to_string()
                    sc = get_portfolio_analysis(client.to_dict(), market_summary)
                    st.session_state['ai_analysis'] = sc
        
        with c_res:
            if st.session_state['ai_analysis']:
                # Boxed result
                st.info(st.session_state['ai_analysis'], icon="💡")
            else:
                st.caption("AI Insight will appear here.")

    st.markdown("---")

    # ---------------------------------------------------------
    # 3. Agentic Workflows (Tabs)
    # ---------------------------------------------------------
    st.subheader("⚡ Agentic Tools")
    
    t1, t2, t3, t4 = st.tabs(["📰 News Impact", "📅 Meeting Prep", "⚠️ Black Swan Simulator", "🧠 Strategy Crew"])
    
    # Tab 1: News
    with t1:
        if st.button("Scan Market News"):
            with st.spinner("Fetching global news..."):
                tickers = list(portfolio.keys())
                news_items = []
                for t in tickers:
                    news_items.extend(get_market_news(t))
                impact_analysis = analyze_news_impact(news_items[:5], portfolio, api_key=api_key)
                st.session_state['news_impact'] = impact_analysis
        
        if st.session_state['news_impact']:
            st.markdown(st.session_state['news_impact'])

    # Tab 2: Meeting
    with t2:
        if st.button("Draft Meeting Agenda"):
             with st.spinner("Drafting..."):
                agenda = generate_meeting_agenda(client.to_dict(), api_key=api_key)
                st.session_state['meeting_agenda'] = agenda
        
        if st.session_state['meeting_agenda']:
            st.success("Draft Ready:")
            st.text_area("Agenda", st.session_state['meeting_agenda'], height=200)

    # Tab 3: Black Swan
    with t3:
        st.write("Simulate a market shock.")
        scenario_input = st.text_input("Scenario", placeholder="e.g. 'Tech Sector crash 15%'")
        if st.button("Run Simulation"):
             with st.spinner("Simulating..."):
                sim_res = run_scenario_simulation(portfolio, scenario_input, client.to_dict(), api_key=api_key)
                st.markdown(sim_res)

    # Tab 4: CrewAI
    with t4:
        st.write("**Autonomous Strategy Team:** Market Analyst + Risk Manager + Wealth Manager")
        if st.button("Activate Strategy Crew"):
            # Status Container for Real-time Feedback
            status_container = st.empty()
            
            def update_status_ui(msg):
                with status_container.container():
                     # Use st.toast or st.info for live updates
                    st.toast(msg, icon="🤖")
                    status_container.info(msg, icon="🤖")

            with st.spinner("Initializing Strategy Team..."):
                tickers = list(portfolio.keys())
                market_summary = get_market_data(tickers).to_string()
                
                results = run_crew_analysis(
                    client.to_dict(), 
                    portfolio, 
                    market_summary, 
                    api_key=api_key, 
                    status_callback=update_status_ui
                )
                
                # Clear status
                status_container.empty()
                st.toast("Strategy Team Completed!", icon="✅")
                
                # Nested Tabs for Crew
                ct1, ct2, ct3 = st.tabs(["Analyst", "Risk", "Manager"])
                
                with ct1:
                    try:
                        d = json.loads(results.get("Market Analyst", "{}"))
                        st.subheader("🚀 Opportunities")
                        st.dataframe(pd.DataFrame(d.get("opportunities", [])))
                        st.subheader("⚠️ Threats")
                        st.dataframe(pd.DataFrame(d.get("threats", [])))
                    except:
                        st.write(results.get("Market Analyst"))
                with ct2:
                    try:
                        d = json.loads(results.get("Risk Manager", "{}"))
                        st.metric("Risk Score", d.get("risk_score"))
                        st.write(f"**Summary:** {d.get('summary')}")
                        st.write("**Concerns:**")
                        for c in d.get("concerns", []):
                            st.markdown(f"- {c}")
                    except:
                        st.write(results.get("Risk Manager"))
                with ct3:
                    st.markdown(results.get("Wealth Manager"))

    # ---------------------------------------------------------
    # 4. Report Generation
    # ---------------------------------------------------------
    st.markdown("---")
    if st.button("📄 Generate PDF Report"):
        from fpdf import FPDF
        import tempfile
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'WealthPilot Client Report', 0, 1, 'C')
            
            def chapter_title(self, title):
                self.set_font('Arial', 'B', 12)
                self.ln(5)
                self.cell(0, 10, title, 0, 1, 'L')
                self.ln(2)

            def chapter_body(self, body):
                self.set_font('Arial', '', 10)
                body = body.encode('latin-1', 'replace').decode('latin-1')
                self.multi_cell(0, 5, body)
                self.ln()

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt=f"Client: {client['Surname']}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Risk Profile: {client['RiskProfile']}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Total AUM: ${client['Balance']:,.2f}", ln=1, align='L')
        
        pdf.chapter_title("Portfolio Holdings")
        for ticker, value in portfolio.items():
            pdf.cell(200, 10, txt=f"{ticker}: ${value:,.2f}", ln=1, align='L')
            
        if st.session_state.get('ai_analysis'):
            pdf.chapter_title("AI Portfolio Analysis")
            pdf.chapter_body(st.session_state['ai_analysis'])
            
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("Download PDF", f, file_name=f"{client['Surname']}_Report.pdf")


elif page == "Market Intelligence":
    st.title("Market Intelligence")
    st.markdown("Real-time market tracking for wealth strategies.")
    
    # Ticker names mapping
    ticker_names = {
        "SPY": "S&P 500 ETF",
        "QQQ": "Nasdaq 100 ETF",
        "IWM": "Russell 2000 ETF",
        "GLD": "Gold ETF",
        "BND": "Bond ETF",
        "BTC-USD": "Bitcoin"
    }
    
    tickers = list(ticker_names.keys())
    data = get_market_data(tickers)
    
    if not data.empty:
        # Add full name column
        data['Name'] = data['Ticker'].map(ticker_names)
        data = data[['Ticker', 'Name', 'Price', 'Change', 'PctChange']]
        st.dataframe(data, width='stretch')
        
        # Price History Chart
        st.subheader("Price History")
        
        # Create selectbox options with full names
        ticker_options = [f"{t} - {ticker_names[t]}" for t in tickers]
        sel_option = st.selectbox("Select Ticker for Detail", ticker_options)
        sel_ticker = sel_option.split(" - ")[0]
        
        # Fetch history
        history = get_ticker_history(sel_ticker, period="1mo")
        
        if not history.empty:
            fig_history = px.line(history, x='Date', y='Close', title=f'{ticker_names[sel_ticker]} - 1 Month Price History')
            fig_history.update_layout(xaxis_title="Date", yaxis_title="Price (USD)")
            st.plotly_chart(fig_history, width='stretch')
            
            # Also show current price metric
            row = data[data['Ticker'] == sel_ticker].iloc[0]
            st.metric(ticker_names[sel_ticker], f"${row['Price']}", f"{row['PctChange']}%")
        else:
            st.warning(f"Unable to fetch history for {sel_ticker}")
    else:
        st.warning("Unable to fetch market data.")
