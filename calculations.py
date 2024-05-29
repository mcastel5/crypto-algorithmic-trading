import pandas as pd
import numpy as np
import pandas_ta
data = pd.read_csv('cryptodata.csv')
data['date'] = pd.to_datetime(data['date'])
data = data.set_index(['date','symbol'])

data['garman_klass_vol'] = ((np.log(data['high'])-np.log(data['low']))**2)/2-(2*np.log(2)-1)*((np.log(data['close'])-np.log(data['open']))**2)

data['rsi'] = data.groupby(level=1)['close'].transform(lambda x: pandas_ta.rsi(close=x, length=20)) # length indicates 20 period window for calculations


def apply_bbands(group):
    bb = pandas_ta.bbands(close=np.log1p(group['close']), length=20)
    if bb is not None:
        group['bb_low'] = bb['BBL_20_2.0']
        group['bb_mid'] = bb['BBM_20_2.0']
        group['bb_high'] = bb['BBU_20_2.0'] 
    else:
        group['bb_low'] = np.nan
    return group


data = data.groupby(level=1,group_keys=False).apply(apply_bbands)

def apply_atr(group):
    atr = pandas_ta.atr(high=group['high'], low=group['low'], close=group['close'], length=14)

    if atr is not None:
        group['atr'] = atr.sub(atr.mean()).div(atr.std())  # Assuming the atr is a Series
    else:
        group['atr'] = np.nan  # Handle the case where atr is None
    return group

data = data.groupby(level=1,group_keys=False).apply(apply_atr)


def compute_macd(group):
    try:
        macd = pandas_ta.macd(close=group['close'], fast=12, slow=26, signal=9)
        if macd is not None and not macd.empty:
            macd = macd.sub(macd.mean()).div(macd.std())
            group['macd'] = macd['MACD_12_26_9']
            print("not empty")

        else:
            print(f"{group.name} MACD computation returned NaN")
            group['macd'] = np.nan
    except Exception as e:
        print(f"Error processing group {group.name}: {e}")
        group['macd'] = np.nan
    return group

data = data.groupby(['symbol'], group_keys=False).apply(compute_macd)
data['dollar_volume'] = (data['close']*data['volume'])/1e6


data = data.dropna()

data.to_csv("calculations.csv")


"""
Error management and if statements correct issues arising from small data-pool. Such issues dissapear with sufficiently large data set.
"""

