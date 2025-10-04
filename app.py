import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import analysis  # import delle funzioni che hai scritto

st.set_page_config(page_title="Finance Analyzer", layout="wide")

st.title("📊 Finance Analyzer")
st.markdown("Analyze company financials, ratios, and trends using **Yahoo Finance** data.")

# Sidebar
ticker = st.sidebar.text_input("Enter company ticker:", "AAPL").upper()
run_analysis = st.sidebar.button("Run Analysis")

if run_analysis:
    with st.spinner(f"Fetching financials for {ticker}..."):
        financials, balance_sheet, cashflow, ratios = analysis.analyze_company(ticker)

    if financials is not None:
        st.subheader(f"Income Statement - {ticker}")
        st.dataframe(financials)

        st.subheader(f"Balance Sheet - {ticker}")
        st.dataframe(balance_sheet)

        st.subheader(f"Cash Flow - {ticker}")
        st.dataframe(cashflow)

        st.subheader(f"Financial Ratios & Indicators - {ticker}")
        st.dataframe(ratios)

        # Plot charts
        st.subheader("📈 Trends over Time")
        for col in ratios.columns:
            fig, ax = plt.subplots(figsize=(7,4))
            ratios[col].plot(marker="o", ax=ax, title=f"{col} over time")
            ax.set_xlabel("Year")
            ax.set_ylabel(col)
            ax.grid(True)
            st.pyplot(fig)
