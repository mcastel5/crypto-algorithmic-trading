import pandas as pd

data = pd.read_csv('calculations.csv',parse_dates=['date'])
data = data.set_index(['date','symbol'])

def calculate_returns(df):

    outlier_cutoff = 0.005  #cutoff for outliers (99.5 percentile)

    lags = [1, 2, 3, 6, 9, 12] # month lags to calculate momentum patterns

    for lag in lags:
        df[f'return_{lag}m'] = (df['close']  # return column for each lag
                              .pct_change(lag) # calculates percentage change between current value and value at specifies number of periods (lags) before
                              .pipe(lambda x: x.clip(lower=x.quantile(outlier_cutoff),
                                                     upper=x.quantile(1-outlier_cutoff))) # remove outliers
                              .add(1) # +1 to percentage change for compounded growth rate calculations (5% = 1.05)
                              .pow(1/lag) # anualizes returns for lags in months
                              .sub(1)) # returns to percentage
    return df
data = data.groupby(level=1, group_keys=False).apply(calculate_returns).dropna() #group by ticker, after applying function
data.info()
data.to_csv('features.csv')