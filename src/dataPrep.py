"""
    Author: Kenneth Chau
    Name: dataPrep.py
    Description: This script contain the class to prepare data for the dash dashboard
"""

import pandas as pd
import cred
import requests

class Portfolio:
    def __init__(self, path):
        df = pd.read_json(path)

        # Set the original df as the trading record table
        self.dfStockPortRecords = df.sort_values(by='Date', ascending = False)
        
        # Build the stock portfolio overview table, this table will show the live data of each stock price
        df['Total Cost'] = df['Quantity'] * df['Cost']
        dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
        dfStockPortOver['Average Cost'] = dfStockPortOver['Total Cost']/dfStockPortOver['Quantity']
        dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Average Cost", "Total Cost"]]
        self.dfStockPortOver = dfStockPortOver.rename(columns = {"Total Cost": "Book Cost"})
        currentPrices = self.latestPrice(self.returnUniqueHold())
        self.dfStockPortOver = self.updatePrices(self.dfStockPortOver, currentPrices)
        self.dfStockPortOver = self.dfStockPortOver.sort_values(by = "Market Value", ascending = False)

    def returnTable(self, choice:str)->pd.DataFrame:
        match choice:
            case 'Overview':
                return self.dfStockPortOver.head(5)
            case 'records':
                return self.dfStockPortRecords.head(10)
            case _:
                return None

    # This is the function that will update the price of the table
    def updatePrices(self, currentDf:pd.DataFrame, currentPrice:dict)->pd.DataFrame:
        def applyUpdatesPrices(item):
            try:
                if len(currentDf) == 1:
                    return float(currentPrice['price'])
                else: 
                    return float(currentPrice[item]['price'])
            except KeyError:
                return currentDf[currentDf['Symbol'] == item]['Average Cost'].values[0]
        currentDf['Current Price'] = currentDf['Symbol'].apply(applyUpdatesPrices)
        currentDf['Market Value'] = currentDf['Current Price'] * currentDf['Quantity']
        currentDf['Unrealized Gain or Loss'] = currentDf['Market Value'] - currentDf['Book Cost']
        currentDf['% Change'] = (currentDf['Market Value']/currentDf['Book Cost'] - 1)*100
        return currentDf


    # This is the function that will return the latest price
    def latestPrice(self, stockList:list)->dict:
        listOfTicker = stockList
        # since the api take comma separated values, we will need to format them like so
        listOfTicker_str = ','.join(listOfTicker)
        api_key = cred.api_key
        base_url = cred.base_url
        tickerPrices = requests.get(base_url.format('price',listOfTicker_str, api_key))
        if tickerPrices.status_code == 200:
            return tickerPrices.json()
        else:
            return tickerPrices.status_code

    def returnBookCost(self)->float:
        return self.dfStockPortOver['Book Cost'].sum()

    def returnMarketValue(self)->float:
        return self.dfStockPortOver['Market Value'].sum()
    
    def returnUnrealizeGainOrLoss(self)->list:
        value = self.dfStockPortOver['Market Value'].sum()- self.dfStockPortOver['Book Cost'].sum()
        if value > 0:
            return value, "positiveNumber"
        else:
            return value, "negativeNumber"
    
    def returnUniqueHold(self)->list:
        return self.dfStockPortOver.Symbol.unique().tolist()
