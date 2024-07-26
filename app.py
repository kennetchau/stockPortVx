#!/usr/bin/env python3

"""
    This is a simple dashboard use to track portfolio prices
    build using dash
    Author: Kenneth Chau
"""
from datetime import datetime
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import cred
import requests
import plotly.express as px
import dash_bootstrap_components as dbc

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

def main():
        currentDateAndTime = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        PortFolio = Portfolio("data/data.json")
        
        dfDis = PortFolio.returnTable('Overview')

        # Create table
        money = dash_table.FormatTemplate.money(2)
        columns = [
                dict(id = 'Symbol', name = 'Symbol'),
                dict(id = 'Quantity', name = 'Quantity'),
                dict(id = 'Average Cost', name = 'Average Cost', type = 'numeric', format = money),
                dict(id = 'Current Price', name = 'Current Price', type = 'numeric', format = money),
                dict(id = 'Book Cost', name = 'Book Cost', type = 'numeric', format = money),
                dict(id = 'Market Value', name = 'Market Value', type = 'numeric', format = money),
                dict(id = 'Unrealized Gain or Loss', name = 'Unrealized Gain or Loss', type = 'numeric', format = money),
                ]

        # Initialize the App
        app = Dash(__name__, external_stylesheets = [dbc.themes.ZEPHYR])
        app.title = "Stock Portfolio"

        # Create the app layout
        app.layout = [
                    html.Div(children = [
                                        html.H2(children =[html.Img(src = 'assets/logos/stock-ticker-svgrepo-com.svg'),
                                                           "Stock Portfolio"],
                                                id = 'Header'),
                                         ],
                             className = "Header"
                             ),
                    
                    html.Div(
                    children = [
                        html.Div(
                            children = [
                                        html.Div(
                                            children = [
                                                html.Div(
                                                    children = [
                                                        html.H3(children = 'Book Cost' , id = "BookCostTitle"),
                                                        html.Div(
                                                            children = [
                                                                '$ {:0,.2f} USD'.format(PortFolio.returnBookCost())
                                                                ],
                                                                id = 'BookCost_Value',
                                                                className = 'Summary_Value'
                                                            ),
                                                        ],
                                                    className = 'Summary_Value_Container'
                                                ),
                                                html.Div(
                                                    children = [
                                                            html.H3(children = 'Market Value' , id = "MarketValueTitle" ),
                                                            html.Div(
                                                                children = [
                                                                    '$ {:0,.2f} USD'.format(PortFolio.returnMarketValue())
                                                                    ],
                                                                    id = 'Market_Value',
                                                                    className = 'Summary_Value'
                                                            ),
                                                        ],                                                        
                                                    className = 'Summary_Value_Container'
                                                ),
                                                html.Div(
                                                        children = [
                                                            html.H3(children = 'Unrealized Gain or Loss' , id = "UnrealizedGainOrLossTitle" ),
                                                            html.Div(
                                                                children = [
                                                                    '$ {:0,.2f} USD'.format(PortFolio.returnUnrealizeGainOrLoss()[0])
                                                                    ],
                                                                    id = 'UGainOrLoss_Value',
                                                                    className = 'Summary_Value' + ' ' + PortFolio.returnUnrealizeGainOrLoss()[1]
                                                            )
                                                        ],
                                                    className = 'Summary_Value_Container'
                                                ),
                                                ]
                                            ),
                                        ],
                            id = 'Portfolo',
                            className = 'flex-child'
                        ),
                        html.Div(
                            children = [
                                dcc.RadioItems(
                                        options = ['Market Value', 'Book Cost', 'Unrealized Gain or Loss'],
                                        value = 'Market Value',
                                        id = 'barChartControl'),
                                dcc.Graph(figure = {},
                                          id = 'SummaryGraph',
                                          className = 'flex-child'
                                          )
                                ],
                            className = 'flex-child'
                            )
                        ],
                    id = 'SummarySection',
                    className = 'flex-container'
                        ),

                    html.Div(
                            children = [
                            html.H3(children = "Portfolio Overview", id = 'PortSum_Title'),
                            dash_table.DataTable(
                            columns = columns, 
                             data=dfDis.to_dict('records'), 
                             page_size = 10,
                             sort_action = 'native',
                            filter_action = 'native', id = "PortSum",
                            style_header = {
                                'fontWeight':'bold',
                                'textAlign': 'center',
                                },
                            style_cell={'textAlign': 'center',
                                        'padding':'3px'},
                            style_as_list_view = True,

                            )],

                            id = "PortOverview"
                        ),
                    
                    html.Div(
                            children = [
                                html.P(children = f"Data refresh at {currentDateAndTime}"),
                                html.P(children = "Data source: twelve data")
                                ],
                            id = "footer"
                        )
                    ]

        # Add Simple call back for selecting book cost or quantity
        @callback (
                Output(component_id = 'SummaryGraph', component_property = 'figure'),
                Input(component_id = 'barChartControl', component_property = 'value'),
        )
        def update_graph(col_chosen):
            dfEdit = dfDis.sort_values(by = col_chosen, ascending = True)
            figure = px.histogram(dfEdit,
                                x=col_chosen,
                                y='Symbol',
                                histfunc = 'sum',
                                )
            return figure
        
        app.run(debug = True)

if __name__ == '__main__':
    main()
