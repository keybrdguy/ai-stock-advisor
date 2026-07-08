import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="AI Stock Practice Advisor", layout="wide", initial_sidebar_state="expanded")

st.title("🤖 AI Stock Practice Advisor")
st.caption("Educational tool for practice trading • NOT financial advice")

# Sidebar
st.sidebar.header("Settings")
risk_level = st.sidebar.selectbox("Risk Profile", ["conservative", "balanced", "aggressive"], index=1)
period = st.sidebar.selectbox("Data Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

# Default tickers
default_tickers = ["AAPL", "MSFT", "NVDA", "SPY", "QQQ", "GLD", "SLV"]

def get_recommendation(df):
    """Super safe recommendation logic"""
    if df.empty or len(df) < 30:
        return "HOLD", 50, "Insufficient data"
    
    close = df["Close"]
    current_price = float(close.iloc[-1])
    recent_mean = float(close.tail(20).mean())
    
    score = 1 if current_price > recent_mean else -1
    
    if score > 0:
        return "BUY", 65, "Price above recent average"
    else:
        return "HOLD", 50, "Mixed or downtrend signals"

def calculate_rsi(data, window=14):
    """Safe RSI calculation returning scalar"""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi_series = 100 - (100 / (1 + rs))
    return float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Watchlist / Scanner", "📈 Custom Analysis", "💼 Virtual Portfolio", "🛡️ Risk Tools", "📉 Backtester"])

with tab1:
    st.subheader("Watchlist & Auto Scanner")
    tickers = st.multiselect("Select or add tickers", default_tickers, default=default_tickers)
    if st.button("Analyze Watchlist"):
        with st.spinner("Fetching data..."):
            results = []
            for ticker in tickers:
                try:
                    df = yf.download(ticker, period=period, progress=False)
                    if not df.empty:
                        rec, conf, reason = get_recommendation(df)
                        results.append({
                            "Ticker": ticker,
                            "Price": round(df["Close"].iloc[-1], 2),
                            "Recommendation": rec,
                            "Confidence": f"{conf}%",
                            "Reason": reason
                        })
                except Exception as e:
                    st.error(f"Error with {ticker}: {e}")
            if results:
                st.dataframe(pd.DataFrame(results))
                st.success("Analysis complete!")
            else:
                st.warning("No data retrieved.")

with tab2:
    st.subheader("📈 Custom Ticker Analysis")
    ticker = st.text_input("Enter ticker symbol (e.g. AAPL, SPY, LLY)", "SPY").upper().strip()
    
    if st.button("Get Full Analysis"):
        with st.spinner("Analyzing..."):
            try:
                df = yf.download(ticker, period=period, progress=False)
                if df.empty:
                    st.error("No data found for this ticker.")
                else:
                    rec, conf, reason = get_recommendation(df)
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("Recommendation", rec, f"{conf}% confidence")
                        st.write(f"**Reason:** {reason}")
                    
                    with col2:
                        st.subheader("Key Stats")
                        close = df["Close"].iloc[-1]
                        st.metric("Current Price", f"${close:.2f}")
                        st.metric("RSI (14)", f"{calculate_rsi(df['Close']):.1f}")
                    
                    # Interactive Chart
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                      row_heights=[0.7, 0.3], vertical_spacing=0.05)
                    
                    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close Price"), row=1, col=1)
                    fig.add_trace(go.Scatter(x=df.index, y=df["Close"].rolling(50).mean(), name="SMA 50"), row=1, col=1)
                    
                    fig.add_trace(go.Scatter(x=df.index, y=calculate_rsi(df["Close"].rolling(14).apply(lambda x: x[-1] if len(x)>0 else np.nan, raw=False)), name="RSI"), row=2, col=1)
                    
                    fig.update_layout(height=600, title=f"{ticker} Technical Analysis")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.error("⚠️ **IMPORTANT RISK WARNING**: This is for educational practice only. Never trade real money based on these signals. Past performance is not indicative of future results.")
                    
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

with tab3:
    st.subheader("💼 Virtual Portfolio (Practice)")
    st.info("Full portfolio tracker available in the desktop Python version. Use Risk Tools here for now.")

with tab4:
    st.subheader("🛡️ Risk Management Tools")
    # Position Sizing
    st.subheader("Position Sizing Calculator")
    col1, col2 = st.columns(2)
    with col1:
        account = st.number_input("Practice Account Size ($)", value=10000, step=1000)
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    with col2:
        entry = st.number_input("Entry Price ($)", value=100.0, step=0.5)
        stop = st.number_input("Stop-Loss Price ($)", value=95.0, step=0.5)
        target = st.number_input("Take-Profit Price ($)", value=110.0, step=0.5)

    if st.button("Calculate Position"):
        risk_amount = account * (risk_pct / 100)
        risk_per_share = abs(entry - stop)
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
            st.success(f"**Recommended Shares: {shares}**")
            st.metric("Max Risk", f"${risk_amount:.2f}")
            rr = abs(target - entry) / risk_per_share if risk_per_share > 0 else 0
            st.metric("Risk-Reward Ratio", f"1:{rr:.1f}")
        st.error("⚠️ **RISK WARNING**: This is practice only. Always use proper risk management.")

    # Correlation
    st.divider()
    st.subheader("Portfolio Correlation Analysis")
    corr_tickers = st.text_input("Tickers (comma separated)", "SPY, QQQ, GLD, TLT").upper()
    if st.button("Analyze Correlations"):
        # (existing correlation code)
        st.info("Correlation matrix would go here (full version in desktop).")

with tab5:
    st.subheader("📉 Backtester")
    st.info("Backtesting features available in the desktop version.")

st.caption("Mobile-optimized for iPhone • Full features in desktop Python version")