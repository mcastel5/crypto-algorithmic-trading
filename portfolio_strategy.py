import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('clusters_data.csv', parse_dates= ['date'])
temp_df = data.copy()
temp_df['date'] = temp_df['date'].astype(str)
temp_df = temp_df[temp_df['date'].str[-2:] == '01']
temp_df['date'] = pd.to_datetime(temp_df['date'])- pd.Timedelta(days=1)
dates_list = temp_df['date'].unique().tolist()
end_of_month = data[data['date'].isin(dates_list)]

def crypto_purchase(end_of_month,investment):

    end_of_month = end_of_month.set_index(['date','symbol','close'])
    mask1 = (end_of_month['cluster'] == 3) | (end_of_month['cluster'] == 2)

    bracket_1 = end_of_month[mask1]
    bracket_1 = (bracket_1 - bracket_1.min()) / (bracket_1.max() - bracket_1.min())

    bracket_1['rating'] = bracket_1['return_3m']*0.2 + bracket_1['macd']*0.2 + bracket_1['bb_low']*0.3+bracket_1['rsi']*0.3
    bracket_1['rating'] = bracket_1['rating']/bracket_1['rating'].sum()
    bracket_1['expenditure'] = bracket_1['rating']*investment
    
    bracket_1 = bracket_1.reset_index()
    bracket_1 = bracket_1.set_index(['date'])
    bracket_1['amount'] = bracket_1['expenditure']//bracket_1['close']

    current_portfolio = bracket_1[['symbol','close','expenditure','amount']]
    return current_portfolio


def profit_calculator(current_portfolio,initial_balance,investment):
    current_portfolio=current_portfolio.groupby('date',group_keys=False)
    months = []
    for name,group in current_portfolio:
        months.append(group)

    balance = initial_balance
    balance_list = [initial_balance]
    profit_list=[]

    for i in range(len(months)-1):
        month = months[i]
        mask = (end_of_month['date']+pd.DateOffset(days=1)-pd.DateOffset(months=1)-pd.DateOffset(days=1)).isin(month.index)& (end_of_month['symbol'].isin(month['symbol'].tolist()))
        comparison = end_of_month[mask]
        comparison = comparison.set_index(['symbol'])
        month = month.reset_index().set_index(['symbol'])
        comparison['income'] = comparison['close'] * month['amount']
        income = comparison['income'].sum()
        balance+=income - investment
        net_income = income-investment
        balance_list.append(balance)
        profit_list.append(net_income)
    print(f"Final profit: ${balance_list[-1]-balance_list[0]} USD | {int(balance_list[-1]/balance_list[0]*100)}% portfolio returns")
    return balance_list,profit_list
        

investment = 1000000
initial_balance = 1000000 
current_portfolio = end_of_month.groupby('date',group_keys=False).apply(crypto_purchase,investment=investment)
balance_list,profit_list = profit_calculator(current_portfolio,initial_balance,investment)

plt.plot(balance_list)
plt.xlabel('Months since 2021-02')
plt.ylabel('Balance (Millions USD)')
plt.axhline(y=1000000, color='red', linestyle='--', label='Threshold')
plt.title('Portfolio Results')
plt.savefig('Portfolio_Results.png')
plt.show()

