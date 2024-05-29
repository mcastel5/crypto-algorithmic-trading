import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

data = pd.read_csv('features.csv',parse_dates=['date'])
data = data.set_index(['date','symbol'])
data.info()
data = data.iloc[:,3:]
data = data.drop(columns= ['volume','trade_count'])
data.info()


target_rsi_values = [30,45,55,70]
initial_centroids = np.zeros((len(target_rsi_values),16)) # we have 16 columns of features
initial_centroids[:, 3] = target_rsi_values  #4rd colum is rsi values

def get_clusters(df):
    df['cluster'] = KMeans(n_clusters=4,
                           random_state=0,
                           init=initial_centroids).fit(df).labels_ 
    return df

data = data.dropna().groupby('date',group_keys=False).apply(get_clusters)

# Calculations for portfolio strategy
data['daily_return'] = data.groupby('symbol')['bb_mid'].pct_change()
cluster_mean_returns = data.groupby(['cluster', 'symbol'])['daily_return'].mean().unstack()
cluster_cov_matrix = {cluster: data[data['cluster'] == cluster].pivot_table(index='date', columns='symbol', values='daily_return').cov() for cluster in data['cluster'].unique()}
data = data.dropna(subset=['daily_return'])
data['atr'] = data['atr'].abs()

data.to_csv('clusters_data.csv')