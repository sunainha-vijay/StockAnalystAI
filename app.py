import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf
from financial_analyst import financial_analyst

# Streamlit UI
st.title("📈 Stock Analyst AI")
st.write("Analyze stocks with AI-driven insights!")

# User input
request = st.text_input("Enter a stock name or request (e.g., 'Analyze Google Stock')")

if st.button("Analyze"):
    if request:
        st.write("Processing your request... 🔍")
        
        # Get investment thesis & stock data
        investment_thesis, hist = financial_analyst(request)
        
        # Display investment thesis
        st.subheader("📊 Investment Thesis / Recommendation")
        st.write(investment_thesis)

        # Plot stock evolution if available
        if hist is not None and not hist.empty:
            st.subheader("📈 Stock Evolution")
            fig, ax = plt.subplots(figsize=(10, 5))
            hist["Close"].plot(ax=ax, title="Stock Closing Prices Over Time")
            st.pyplot(fig)
        else:
            st.write("No stock data available.")

    else:
        st.warning("⚠️ Please enter a valid stock request.")

# Run with: `streamlit run streamlit_app.py`
