import streamlit as st
import pandas as pd
import altair as alt
import alpha_vantage    
from urllib.error import URLError
import requests
import datetime
import numpy as np
import json


def get_historical_data(user_input_list):    # get the stock info for a given stock symbol, month, and year
	
	symbol, selected_month, selected_year = user_input_list

	API_KEY = open('API_key.txt').read()    # get API key stored in text doc (you must get the key from AlphaVantage)
	API_URL = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={API_KEY}&outputsize=full'
	response = requests.get(API_URL)    # request the desired stock info from AlphaVantage 
	raw = response.json()
	
	try: 
		raw_df = pd.DataFrame(list(raw['Time Series (Daily)'].items()), columns = ['Date','Values'])    # nested dict comes back,
																										# pull out (Time Series Daily))
	except KeyError as e:
		return None
																								
	df = pd.concat([raw_df.drop(['Values'], axis=1), raw_df['Values'].apply(pd.Series)], axis=1)    # flatten the nested dict (Values is another dict)
	# print(raw_df)
	df = df.rename(columns = {'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adj close', '6. volume': 'volume'})
	df['Symbol'] = pd.Series([symbol for x in range(len(df.index))])   # add a col holding the ticker symbol

	cols=[i for i in df.columns if i not in ["Date", "Symbol"]]    # convert all the cols except Date and Symbol to numeric
	for col in cols:
		df[col]=pd.to_numeric(df[col])

	df.Date = pd.to_datetime(df.Date)    # convert Date col to datetime type
	df['month'] = df['Date'].dt.month    # extract month from Date col ---> used to subset
	df['year'] = df['Date'].dt.year      # extract year from Date col ---> used to subset
	df = df.iloc[::-1].drop(['7. dividend amount', '8. split coefficient'], axis = 1)    # drop unnecessary cols
	df = df[['year', 'month', 'Date', 'open', 'high', 'low', 'close', 'adj close', 'volume', 'Symbol']]    # re-order df cols in desired order
	subsetted = df.loc[(df['year'] == selected_year) & (df['month'] == selected_month)]    # subset df based on query (which gives a month and year)

	return subsetted


def plot_stock(stock_data):

	try:
	 	symbol = stock_data.loc[stock_data.index[0], 'Symbol']    # get the symbol out of the df  ---> used in plot
	 	year = stock_data.loc[stock_data.index[0], 'year']    # get the year out of the df ---> used in plot
	 	month = stock_data.loc[stock_data.index[0], 'month']    # get the month out of the df ---> used in plot

	 	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']    # dict to retrieve month names from month #s
	 	month_dict = dict(zip(np.arange(1,13,1), months))
	 	month_name = month_dict.get(np.int64(month))

	 	chart = alt.Chart(stock_data, title=f'{str(symbol)} Daily Closing Values (USD) for {str(month_name)} of {str(year)}').mark_line(point=True).encode(alt.Y('close', scale=alt.Scale(zero=False)), x='Date')
	 	# chart.show()
	 	
	 	return(chart)

	except IndexError as ie:
		st.header("Unable to retrieve data")

	except AttributeError as ae:
		st.header("Unable to retrieve data")


def streamlit_plot(graph):

	try:
		st.altair_chart(graph)
	except AttributeError as e:
		st.subheader("Please enter a valid Stock Ticker, Year, and Month")



def streamlit_initiate():

	current_year = datetime.date.today().year
	last_year = current_year - 1
	year_range = np.arange(start=current_year, stop=(current_year-20), step=-1, dtype = int)
	year_range = year_range.tolist()
	months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	month_dict = dict(zip(months, np.arange(1,13,1)))
	
	st.title("TDI Stock Market Montly Reporter")

	ticker_symbol = st.sidebar.text_input("Enter the ticker symbol:", 'GOOGL')
	default_month_ix = months.index('Jan')    # set a default month of Jan
	selected_month = st.sidebar.selectbox('Select Month', months, index=default_month_ix)

	default_year_ix = year_range.index(last_year) # select a default year of prior year
	selected_year = st.sidebar.selectbox('Select Year', year_range, index=default_year_ix)


	selected_month_num = month_dict[selected_month]

	return [str(ticker_symbol), selected_month_num.item(), selected_year]



def driver():
	user_input_list = streamlit_initiate()
	req_stock_data = get_historical_data(user_input_list)
	stock_graph = plot_stock(req_stock_data)
	streamlit_plot(stock_graph)

driver()








