#!/usr/bin/env python3

"""
    This is a simple dashboard use to track portfolio prices
    build using dash
    Author: Kenneth Chau
"""
from datetime import datetime
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from dataPrep import Portfolio



def layout(app):
        # Get the current time
        currentDateAndTime = datetime.now().strftime("%d %b %Y, %H:%M:%S")
        # Getting the data
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
                            style_data_conditional = [
                                {
                                    'if':{
                                    'filter_query':'{Unrealized Gain or Loss} < 0',
                                    'column_id': 'Unrealized Gain or Loss'
                                        },
                                    'color':'red',
                                },
                                {
                                    'if':{
                                    'filter_query':'{Unrealized Gain or Loss} > 0',
                                    'column_id': 'Unrealized Gain or Loss'
                                        },
                                    'color':'green',
                                }
                            ]
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

        return app.layout

# Create the main function
def main():
        # Initialize the App
        app = Dash(__name__, external_stylesheets = [dbc.themes.ZEPHYR])
        app.title = "Stock Portfolio"
        app.layout = layout(app)
        app.run(debug = True)

if __name__ == '__main__':
    main()
