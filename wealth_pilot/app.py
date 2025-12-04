import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from utils.market_data import get_market_data
from utils.ai_agent import configure_genai, get_portfolio_analysis, chat_with_agent

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
    api_key = st.text_input("Gemini API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        configure_genai(api_key)
        st.success("AI Agent Active")
    else:
        st.warning("Enter API Key to enable AI features")

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
        
    st.dataframe(filtered_df[['CustomerId', 'Surname', 'Age', 'Balance', 'RiskProfile', 'FinancialGoal']], use_container_width=True)
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig_risk = px.pie(df_clients, names='RiskProfile', title='Client Risk Distribution', hole=0.4)
        st.plotly_chart(fig_risk, use_container_width=True)
    with c2:
        fig_geo = px.bar(df_clients, x='Geography', y='Balance', title='AUM by Geography')
        st.plotly_chart(fig_geo, use_container_width=True)

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
            st.dataframe(df_port, use_container_width=True)
            
            fig_port = px.pie(df_port, values='Value', names='Ticker', title='Portfolio Allocation')
            st.plotly_chart(fig_port, use_container_width=True)
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
                st.markdown(analysis)
        
        st.markdown("---")
        st.subheader("Chat with Agent")
        user_query = st.text_input("Ask about this client...")
        if user_query:
            with st.spinner("Thinking..."):
                context = f"Client: {client.to_dict()}\nPortfolio: {portfolio}"
                response = chat_with_agent(user_query, context)
                st.write(response)

    # Report Generation
    st.markdown("---")
    if st.button("Generate Client Report (PDF)"):
        from fpdf import FPDF
        import tempfile
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'WealthPilot Client Report', 0, 1, 'C')
                
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        pdf.cell(200, 10, txt=f"Client: {client['Surname']}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Risk Profile: {client['RiskProfile']}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"Total AUM: ${client['Balance']:,.2f}", ln=1, align='L')
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Portfolio Holdings:", ln=1, align='L')
        pdf.set_font("Arial", size=12)
        
        for ticker, value in portfolio.items():
            pdf.cell(200, 10, txt=f"{ticker}: ${value:,.2f}", ln=1, align='L')
            
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            with open(tmp.name, "rb") as f:
                st.download_button("Download PDF", f, file_name=f"{client['Surname']}_Report.pdf")


elif page == "Market Intelligence":
    st.title("Market Intelligence")
    st.markdown("Real-time market tracking for wealth strategies.")
    
    tickers = ["SPY", "QQQ", "IWM", "GLD", "BND", "BTC-USD"]
    data = get_market_data(tickers)
    
    if not data.empty:
        st.dataframe(data, use_container_width=True)
        
        # Simple chart
        sel_ticker = st.selectbox("Select Ticker for Detail", tickers)
        # In a real app, we'd fetch history here. For now just show the price.
        row = data[data['Ticker'] == sel_ticker].iloc[0]
        st.metric(sel_ticker, f"${row['Price']}", f"{row['PctChange']}%")
    else:
        st.warning("Unable to fetch market data.")
