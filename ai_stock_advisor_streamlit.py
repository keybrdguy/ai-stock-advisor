import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
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

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Watchlist / Scanner", "📈 Custom Analysis", "💼 Virtual Portfolio", "🛡️ Risk Tools", "📉 Backtester"])

with tab1:
    st.subheader("Watchlist & Auto Scanner")
    tickers = st.multiselect("Select or add tickers", default_tickers, default=default_tickers)
    if st.button("Analyze"):
        with st.spinner("Fetching data..."):
            results = []
            for ticker in tickers:
                try:
                    df = yf.Ticker(ticker).history(period=period)
                    if not df.empty:
                        # Simple recommendation logic (simplified from original)
                        close = df["Close"]
                        sma50 = close.rolling(50).mean().iloc[-1] if len(close) > 50 else None
                        rsi = 50  # Placeholder - implement full if needed
                        rec = "BUY" if close.iloc[-1] > (sma50 or close.iloc[-1]) else "HOLD"
                        results.append({"Ticker": ticker, "Price": close.iloc[-1], "Rec": rec})
                except:
                    st.error(f"Error with {ticker}")
            if results:
                st.dataframe(pd.DataFrame(results))

with tab2:
    st.subheader("Custom Ticker Analysis")
    ticker = st.text_input("Enter ticker", "SPY").upper()
    if st.button("Get Analysis"):
        st.info("Full analysis coming in future update - for now showing chart")
        df = yf.download(ticker, period=period)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Price"))
        st.plotly_chart(fig)

with tab3:
    st.subheader("Virtual Portfolio (Practice)")
    st.info("Portfolio tracker coming soon — use the desktop version for full features in the meantime.")

with tab4:
    st.subheader("🛡️ Full Risk Calculator")
    st.caption("Position sizing + Risk-Reward analysis (practice only)")

    col1, col2 = st.columns(2)
    with col1:
        account = st.number_input("Practice Account Size ($)", value=10000, step=1000)
        risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    
    with col2:
        entry = st.number_input("Entry Price ($)", value=100.0, step=0.5)
        stop = st.number_input("Stop-Loss Price ($)", value=95.0, step=0.5)
        target = st.number_input("Take-Profit Price ($)", value=110.0, step=0.5)

    if st.button("Calculate Risk & Position"):
        risk_amount = account * (risk_pct / 100)
        risk_per_share = abs(entry - stop)
        
        if risk_per_share > 0:
            shares = int(risk_amount / risk_per_share)
            position_value = shares * entry
            max_loss = risk_amount
            reward = abs(target - entry)
            rr = reward / risk_per_share if risk_per_share > 0 else 0
            
            st.success(f"**Recommended Shares: {shares}**")
            st.metric("Position Value", f"${position_value:,.2f}")
            st.metric("Max Loss if Stopped", f"${max_loss:,.2f} ({risk_pct}%)")
            st.metric("Risk-Reward Ratio", f"1:{rr:.2f}")
            
            if rr >= 2:
                st.info("✅ Good risk-reward ratio!")
            else:
                st.warning("⚠️ Consider a higher target for better R:R")
        else:
            st.error("Stop price must be different from entry.")
        
        st.error("⚠️ RISK WARNING: Never risk more than 1-2% of total capital per trade. This is for educational practice only.")

    st.divider()
    st.subheader("📊 Portfolio Correlation Analysis")
    st.caption("See how your holdings move together (diversification insight)")

    corr_tickers = st.text_input("Tickers (comma separated)", "SPY, QQQ, GLD, TLT").upper().replace(" ", "")
    corr_period = st.selectbox("Correlation Period", ["1y", "2y", "5y"], index=1)

    if st.button("Analyze Correlations"):
        tickers_list = [t.strip() for t in corr_tickers.split(",") if t.strip()]
        if len(tickers_list) < 2:
            st.warning("Enter at least 2 tickers.")
        else:
            with st.spinner("Fetching data..."):
                try:
                    data = yf.download(tickers_list, period=corr_period, progress=False)["Close"]
                    if data.empty:
                        st.error("No data retrieved.")
                    else:
                        returns = data.pct_change().dropna()
                        corr_matrix = returns.corr()
                        
                        st.dataframe(corr_matrix.style.background_gradient(cmap="RdYlGn", axis=None))
                        
                        # Simple interpretation
                        avg_corr = corr_matrix.mean().mean()
                        if avg_corr > 0.7:
                            st.warning("High average correlation — limited diversification benefit.")
                        elif avg_corr < 0.3:
                            st.success("Low average correlation — good diversification.")
                        else:
                            st.info("Moderate correlation — decent diversification.")
                        
                        st.error("⚠️ RISK WARNING: Correlation can change over time, especially in market stress. Diversify across asset classes.")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab5:
    st.subheader("📉 Backtester (Practice)")
    st.caption("Simple SMA Crossover strategy backtest — educational only")
    
    ticker = st.text_input("Ticker for backtest", "SPY").upper()
    backtest_period = st.selectbox("Backtest Period", ["1y", "2y", "5y"], index=1)
    strategy = st.selectbox("Strategy", ["SMA Crossover (50/200)", "RSI Mean Reversion"], index=0)
    
    if st.button("Run Backtest"):
        with st.spinner("Running backtest..."):
            try:
                df = yf.download(ticker, period=backtest_period, progress=False)
                if df.empty:
                    st.error("No data.")
                else:
                    df = df.dropna()
                    close = df["Close"]
                    
                    # Simple SMA Crossover
                    if "SMA" in strategy:
                        sma50 = close.rolling(50).mean()
                        sma200 = close.rolling(200).mean()
                        df["Signal"] = 0
                        df.loc[sma50 > sma200, "Signal"] = 1  # Buy
                        df["Position"] = df["Signal"].shift(1).fillna(0)
                        
                        df["Returns"] = close.pct_change()
                        df["Strategy_Returns"] = df["Position"] * df["Returns"]
                        
                        equity = (1 + df["Strategy_Returns"]).cumprod()
                        bh_equity = (1 + df["Returns"]).cumprod()
                        
                        total_return = equity.iloc[-1] - 1
                        bh_return = bh_equity.iloc[-1] - 1
                        
                        st.metric("Strategy Total Return", f"{total_return*100:.1f}%")
                        st.metric("Buy & Hold Return", f"{bh_return*100:.1f}%")
                        
                        # Equity curve
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index, y=equity, name="Strategy Equity"))
                        fig.add_trace(go.Scatter(x=df.index, y=bh_equity, name="Buy & Hold"))
                        fig.update_layout(title="Equity Curve", xaxis_title="Date", yaxis_title="Growth")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.success("Backtest complete. Strategy performance shown above.")
                    
                    else:
                        st.info("RSI strategy coming soon.")
            except Exception as e:
                st.error(f"Backtest error: {e}")

st.markdown("---")
st.caption("For full console version with all features, use the .py file on a computer. This is a mobile-optimized preview.")