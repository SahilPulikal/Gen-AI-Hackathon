import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from utils.market_data import get_market_data, get_market_news, get_ticker_history
from utils.ai_agent import configure_genai, get_portfolio_analysis, chat_with_agent, analyze_news_impact, generate_meeting_agenda
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
    
    client_id = st.selectbox("Select Client", df_clients['CustomerId'].astype(str) + " - " + df_clients['Surname'])
    selected_id = client_id.split(" - ")[0]
    client = df_clients[df_clients['CustomerId'] == selected_id].iloc[0]
    
    # Client Header
    st.markdown(f"## {client['Surname']} (Age: {client['Age']})")
    st.markdown(f"**Risk Profile:** {client['RiskProfile']} | **Goal:** {client['FinancialGoal']}")
    
    # Portfolio
    portfolio = json.loads(client['Portfolio'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Portfolio")
        if portfolio:
            df_port = pd.DataFrame(list(portfolio.items()), columns=['Ticker', 'Value'])
            st.dataframe(df_port, width='stretch')
            
            fig_port = px.pie(df_port, values='Value', names='Ticker', title='Portfolio Allocation')
            st.plotly_chart(fig_port, width='stretch')
        else:
            st.info("No portfolio data available.")
            
    with col2:
        st.subheader("AI Analysis")
        if st.button("Generate Portfolio Insights"):
            with st.spinner("Analyzing with Gemini..."):
                # Fetch real market data for these tickers
                tickers = list(portfolio.keys())
                market_summary = get_market_data(tickers)
                
                analysis = get_portfolio_analysis(client.to_dict(), market_summary)
                st.session_state['ai_analysis'] = analysis
                st.markdown(analysis)
        elif st.session_state['ai_analysis']:
            st.markdown(st.session_state['ai_analysis'])
        
        st.markdown("---")
        st.subheader("Chat with Agent")
        user_query = st.text_input("Ask about this client...")
        if user_query:
            with st.spinner("Thinking..."):
                context = f"Client: {client.to_dict()}\nPortfolio: {portfolio}"
                response = chat_with_agent(user_query, context)
                st.write(response)

    # New Agentic Features
    st.markdown("---")
    st.subheader("Agentic Workflows")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("Analyze News Impact"):
            with st.spinner("Scanning market news..."):
                # Gather news for all tickers
                all_news = []
                for ticker in portfolio.keys():
                    news = get_market_news(ticker)
                    all_news.extend(news)
                
                if all_news:
                    impact_analysis = analyze_news_impact(all_news[:10], portfolio, api_key=api_key) # Limit to top 10 for speed
                    st.session_state['news_impact'] = impact_analysis
                    st.markdown(impact_analysis)
                else:
                    st.info("No recent news found for portfolio holdings.")
        elif st.session_state['news_impact']:
            st.markdown(st.session_state['news_impact'])

    with col_b:
        if st.button("Prepare Meeting Agenda"):
            with st.spinner("Drafting agenda..."):
                agenda = generate_meeting_agenda(client.to_dict(), api_key=api_key)
                st.session_state['meeting_agenda'] = agenda
                st.markdown(agenda)
        elif st.session_state['meeting_agenda']:
            st.markdown(st.session_state['meeting_agenda'])

    # Report Generation
    st.markdown("---")
    if st.button("Generate Client Report (PDF)"):
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
                # FPDF doesn't support full Markdown or Unicode well by default
                # We'll do basic cleanup
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
            
        if st.session_state.get('news_impact'):
            pdf.chapter_title("News Impact Analysis")
            pdf.chapter_body(st.session_state['news_impact'])
            
        if st.session_state.get('meeting_agenda'):
            pdf.chapter_title("Meeting Agenda")
            pdf.chapter_body(st.session_state['meeting_agenda'])
            
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
