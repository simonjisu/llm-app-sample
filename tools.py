import yfinance
import pandas as pd
from langchain_core.tools import tool
from typing import Any

@tool
def get_ticker_info(ticker: str) -> dict:
    """Get general information for a ticker from Yahoo Finance."""
    ticker = yfinance.Ticker(ticker)
    info = ticker.info
    return info

@tool
def get_income_statement(ticker: str) -> pd.DataFrame:
    """Get income statement for a ticker from Yahoo Finance."""
    ticker = yfinance.Ticker(ticker)
    income_statement = ticker.income_stmt
    return income_statement

@tool
def get_balance_sheet(ticker: str) -> pd.DataFrame:
    """Get balance sheet for a ticker from Yahoo Finance."""
    ticker = yfinance.Ticker(ticker)
    balance_sheet = ticker.balance_sheet
    return balance_sheet

@tool
def get_news(ticker: str) -> list[dict[str, Any]]:
    """Get news for a ticker from Yahoo Finance."""
    ticker = yfinance.Ticker(ticker)
    news = ticker.news
    return news