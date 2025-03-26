import os
import requests
import json
from dotenv import load_dotenv
import yfinance as yf
from yahooquery import Ticker
import google.generativeai as genai
import pandas as pd

# Load environment variables
load_dotenv()

# Set API Keys
serper_api_key = os.getenv("SERP_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def get_company_news(company_name):
    """Fetches latest news for a given company."""
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    data = {'q': company_name}

    response = requests.post('https://google.serper.dev/news', headers=headers, json=data)
    data = response.json()
    return data.get('news', [])


def get_stock_evolution(company_ticker, period="1y"):
    """Fetches stock price history and returns a DataFrame."""
    stock = yf.Ticker(company_ticker)

    try:
        hist = stock.history(period=period)
        if hist.empty:
            print(f"Warning: No historical data found for {company_ticker}")
            return None
    except Exception as e:
        print(f"Error fetching stock data for {company_ticker}: {e}")
        return None

    return hist


def get_financial_statements(ticker):
    """Fetches financial statements for a given company ticker."""
    company = Ticker(ticker)
    try:
        balance_sheet = company.balance_sheet()
        cash_flow = company.cash_flow(trailing=False)
        income_statement = company.income_statement()
        valuation_measures = company.valuation_measures if hasattr(company, "valuation_measures") else "N/A"
    except Exception as e:
        print(f"Error fetching financial statements: {e}")
        return "Error fetching financial data."

    return {
        "Balance Sheet": balance_sheet.to_string() if isinstance(balance_sheet, pd.DataFrame) else str(balance_sheet),
        "Cash Flow": cash_flow.to_string() if isinstance(cash_flow, pd.DataFrame) else str(cash_flow),
        "Income Statement": income_statement.to_string() if isinstance(income_statement, pd.DataFrame) else str(income_statement),
        "Valuation Measures": str(valuation_measures),
    }


import yahooquery as yq

# Extended mapping for well-known companies
KNOWN_COMPANIES = {
    "Google": "GOOGL",
    "Alphabet": "GOOGL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Facebook": "META",
    "Meta": "META",
    "Netflix": "NFLX",
    "NVIDIA": "NVDA",
    "AMD": "AMD",
    "Intel": "INTC",
    "IBM": "IBM",
    "Qualcomm": "QCOM",
    "Cisco": "CSCO",
    "Salesforce": "CRM",
    "Adobe": "ADBE",
    "PayPal": "PYPL",
    "Visa": "V",
    "Mastercard": "MA",
    "JP Morgan": "JPM",
    "Goldman Sachs": "GS",
    "Bank of America": "BAC",
    "Wells Fargo": "WFC",
    "Berkshire Hathaway": "BRK.B",
    "Disney": "DIS",
    "Coca-Cola": "KO",
    "Pepsi": "PEP",
    "McDonald's": "MCD",
    "Starbucks": "SBUX",
    "Nike": "NKE",
    "Toyota": "TM",
    "Ford": "F",
    "General Motors": "GM",
    "Boeing": "BA",
    "Airbus": "AIR.PA",
    "ExxonMobil": "XOM",
    "Chevron": "CVX",
    "Shell": "SHEL",
    "Tesla": "TSLA",
    "Uber": "UBER",
    "Lyft": "LYFT",
    "Zoom": "ZM",
    "Snowflake": "SNOW",
    "Shopify": "SHOP",
    "Alibaba": "BABA",
    "Tencent": "TCEHY",
    "Samsung": "005930.KQ",
    "Sony": "SONY",
}

def get_valid_ticker(company_name):
    """Finds the correct stock ticker for a given company name using Yahoo Finance."""
    
    # Standardize company name (to match keys in the dictionary)
    company_name = company_name.strip().title()

    # Check if the company is in the pre-mapped list
    if company_name in KNOWN_COMPANIES:
        return KNOWN_COMPANIES[company_name]

    # Otherwise, try Yahoo Finance query
    ticker_obj = yq.Ticker(company_name)
    search_results = ticker_obj.quote_type

    print("Search Results:", search_results)  # Debugging

    if search_results:
        for key, value in search_results.items():
            if isinstance(value, dict) and "symbol" in value:
                return value["symbol"]

    return None  # If no valid ticker found

def financial_analyst(request):
    """Main function to analyze stocks based on a user request."""
    print(f"Received request: {request}")

    # Step 1: Get company name and ticker from Gemini
    response = model.generate_content(
        f"Extract the company name from this request: {request}. Provide only the company name."
    )
    company_name = response.text.strip()

    print(f"Extracted Company Name: {company_name}")

    # Step 2: Get the correct stock ticker
    company_ticker = get_valid_ticker(company_name)
    if not company_ticker:
        return f"Could not find a valid ticker for {company_name}. Please try again.", None

    print(f"Validated Ticker: {company_ticker}")

    # Step 3: Fetch data
    hist = get_stock_evolution(company_ticker)
    financials = get_financial_statements(company_ticker)

    # Step 4: Generate Investment Thesis
    second_response = model.generate_content(
        f"""Analyze the stock {company_name} ({company_ticker}).
        Provide a detailed investment thesis with numbers, historical trends, and insights.
        Should we buy, hold, or sell? Be brutally honest.
        Short-term or long-term investment? Reference sources if possible.
        """
    )

    return second_response.text, hist
