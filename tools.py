import time
import os
import pandas as pd
import yfinance as yf
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.retrievers.web_research import WebResearchRetriever

from datetime import datetime as dt

load_dotenv()

# Yahoo Finance API
def info_to_str(info) -> str:
    address = f"{info['address1']}, {info['city']}, {info['state']} {info['zip']}, {info['country']}"
    info_str = f'Address: {address}\n'
    info_str += f'Sector: {info["sector"]}\n'
    info_str += f'Industry: {info["industry"]}\n'
    info_str += f'Website: {info["website"]}\n'
    info_str += f'Phone: {info["phone"]}\n'
    info_str += f'Full Time Employees: {info["fullTimeEmployees"]}\n'
    info_str += f'Long Business Summary: {info["longBusinessSummary"]}\n'
    for x in info['companyOfficers']:
        info_str += f'{x["title"]}: {x["name"]}\n'
    return info_str

@tool
def get_ticker_info(ticker: str) -> dict:
    """Get address, sector industry, employee information for a ticker from Yahoo Finance API."""
    ticker = yf.Ticker(ticker)
    return info_to_str(ticker.info)

@tool
def get_income_statement(ticker: str) -> pd.DataFrame:
    """Get income statement for a ticker from Yahoo Finance API."""
    ticker = yf.Ticker(ticker)
    income_statement = ticker.income_stmt
    return income_statement

@tool
def get_balance_sheet(ticker: str) -> pd.DataFrame:
    """Get balance sheet for a ticker from Yahoo Finance API."""
    ticker = yf.Ticker(ticker)
    balance_sheet = ticker.balance_sheet
    return balance_sheet

def news_to_str(ticker) -> str:
    s = ''
    for x in ticker.news:
        s += f"Title: {x['title']}\n"
        s += f"Publish Time: {dt.fromtimestamp(x['providerPublishTime'])}\n"
        s += f"URL: {x['link']}\n"
        s += f"Related Tickers: {x['relatedTickers']}\n"
    return s

@tool
def get_news(ticker: str) -> str:
    """Get most recent news for a ticker from Yahoo Finance API."""
    ticker = yf.Ticker(ticker)
    return news_to_str(ticker)

@tool
def get_recent_price(ticker: str) -> pd.DataFrame:
    """Get recent 5 dyas price data for a ticker from Yahoo Finance API."""
    ticker = yf.Ticker(ticker)
    return ticker.history(period="5d")

# Google Search
GOOGLE_SEARCH = GoogleSearchAPIWrapper(
    google_cse_id=os.getenv("GOOGLE_CSE_ID"),
)
GOOGLE_SEARCH_ENGINE = {
    "hotels": GoogleSearchAPIWrapper(
        google_cse_id=os.getenv("GOOGLE_CSE_ID_HOTEL"),
    ),
    "restaurants": GoogleSearchAPIWrapper(
        google_cse_id=os.getenv("GOOGLE_CSE_ID_RESTURANT"),
    )
}
def gsearch_tool(query: str) -> dict[str, str]:
    """Search Google for recent results."""
    return GOOGLE_SEARCH.results(query, 1)[0]

def get_google_search_results(response: dict[str, list[str]]) -> dict[str, list[dict[str, str]]]:
    results = {'hotel': [], 'resturant': []}
    for key, search_keywords in response.items():
        for keyword in search_keywords:
            search_res = gsearch_tool(keyword)
            time.sleep(0.25)
            results[key].append({'key': keyword, 'result': search_res})
    return results

# Web Search Retriever
def create_web_retriever(query_type: str, db_path="./chroma_db"):
    embedding_func = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

    vectorstore = Chroma(embedding_function=embedding_func,
                        persist_directory=db_path)

    search_llm = ChatOpenAI(
        model = "gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )

    web_retriever = WebResearchRetriever.from_llm(
        vectorstore=vectorstore,
        llm=search_llm, 
        search=GOOGLE_SEARCH_ENGINE[query_type],
        num_search_results=1
    )
    return web_retriever

def formatting_output(output: dict):
    return [x.replace(',', ' ') + f"  {output['city']}" for x in output["items"]]
