import yfinance as yf
from pprint import pprint

aapl = yf.Ticker('AAPL')
pprint(aapl.news)
print(type(aapl.news))