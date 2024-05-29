from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd

client = CryptoHistoricalDataClient()
crypto_list = ['AAVE', 'AVAX', 'BAT', 'BCH', 'BTC', 'CRV', 'DOT', 'ETH', 'GRT', 'LINK', 'LTC', 'MKR', 'SHIB', 'UNI', 'USDC', 'USDT', 'XTZ']
request_params = CryptoBarsRequest(
  symbol_or_symbols=[f"{x}/USD" for x in crypto_list],
  timeframe=TimeFrame.Day,
  start="2015-01-01",
  end="2024-05-24"
)

# Retrieve daily bars for Bitcoin in a DataFrame and printing it
btc_bars = client.get_crypto_bars(request_params)

# Convert to dataframe
df = btc_bars.df
df.to_csv('cryptodata.csv')

data = pd.read_csv('cryptodata.csv')

data['timestamp'] = pd.to_datetime(data['timestamp'].str.split(' ').str[0])
data.rename(columns={'timestamp':'date'},inplace = True)
data['symbol'] = data['symbol'].str.split('/').str[0]
data = data.set_index('symbol')

data.to_csv("cryptodata.csv")