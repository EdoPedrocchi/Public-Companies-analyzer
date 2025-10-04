import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def analyze_company(ticker):
    company = yf.Ticker(ticker)

    # === Download financial statements ===
    financials = company.financials
    balance_sheet = company.balance_sheet
    cashflow = company.cashflow
    info = company.info

    if financials.empty or balance_sheet.empty or cashflow.empty:
        print(f"❌ No financial data found for ticker: {ticker}")
        return None, None, None, None

    # Keep last 5 years
    cols = financials.columns[:5]
    financials = financials[cols]
    balance_sheet = balance_sheet[cols]
    cashflow = cashflow[cols]

    # === Safe extraction ===
    def safe_get(df, keys):
        if isinstance(keys, str):
            keys = [keys]
        for key in keys:
            if key in df.index:
                return df.loc[key]
        return pd.Series([None]*len(cols), index=cols)

    # Income Statement
    revenues = safe_get(financials, ["Total Revenue", "Operating Revenue"])
    ebit = safe_get(financials, ["EBIT", "Operating Income"])
    net_income = safe_get(financials, ["Net Income", "Net Income Common Stockholders"])

    # Balance Sheet
    total_assets = safe_get(balance_sheet, ["Total Assets"])
    total_liab = safe_get(balance_sheet, ["Total Liabilities Net Minority Interest"])
    equity = safe_get(balance_sheet, ["Stockholders Equity", "Common Stock Equity"])
    current_assets = safe_get(balance_sheet, ["Current Assets"])
    current_liab = safe_get(balance_sheet, ["Current Liabilities"])

    # Cash Flow
    operating_cf = safe_get(cashflow, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
    capex = safe_get(cashflow, ["Capital Expenditure", "Purchase Of PPE"])
    free_cf = safe_get(cashflow, ["Free Cash Flow"])
    if free_cf.isna().all():
        free_cf = operating_cf + capex  # fallback

    # === Ratios per year ===
    ratios = pd.DataFrame(index=cols)

    ratios["Operating Margin (%)"] = (ebit / revenues) * 100
    ratios["Net Margin (%)"] = (net_income / revenues) * 100
    ratios["ROE (%)"] = (net_income / equity) * 100
    ratios["ROA (%)"] = (net_income / total_assets) * 100

    ratios["Debt-to-Equity"] = total_liab / equity
    ratios["Current Ratio"] = current_assets / current_liab

    ratios["Free Cash Flow"] = free_cf

    ratios["Revenue Growth (%)"] = revenues.pct_change(-1) * 100
    ratios["Net Income Growth (%)"] = net_income.pct_change(-1) * 100
    ratios["FCF Growth (%)"] = free_cf.pct_change(-1) * 100

    # Market multiples (only most recent year)
    ratios.loc[cols[0], "P/E Ratio"] = info.get("trailingPE", None)
    ratios.loc[cols[0], "EV/EBITDA"] = info.get("enterpriseToEbitda", None)
    ratios.loc[cols[0], "Price/Sales"] = info.get("priceToSalesTrailing12Months", None)
    ratios.loc[cols[0], "Price/Book"] = info.get("priceToBook", None)

    return financials, balance_sheet, cashflow, ratios


def plot_indicators(ratios, ticker):
    if ratios is None:
        return
    plt.style.use("seaborn-v0_8")
    for col in ratios.columns:
        plt.figure(figsize=(8,5))
        ratios[col].plot(marker="o", title=f"{col} over time - {ticker}")
        plt.xlabel("Year")
        plt.ylabel(col)
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    ticker = input("Enter company ticker (e.g. AAPL, MSFT, TSLA): ").upper()
    financials, balance_sheet, cashflow, ratios = analyze_company(ticker)

    if financials is not None:
        print("\n📊 Income Statement (last 5 years):")
        print(financials)

        print("\n📒 Balance Sheet (last 5 years):")
        print(balance_sheet)

        print("\n💵 Cash Flow (last 5 years):")
        print(cashflow)

        print("\n📈 Key Ratios & Indicators (5 years):")
        print(ratios)

        plot_indicators(ratios, ticker)
