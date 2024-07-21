from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

class Portfolio:
        def __init__(self, path):
            df = pd.read_csv(path)
            df['Book Cost'] = df['Quantity'] * df['Cost']
            dfStockPortOver = df.drop(columns = ['Date']).groupby(by = "Symbol").sum().reset_index(drop=False)
            dfStockPortOver = dfStockPortOver[["Symbol", "Quantity", "Book Cost"]]
            dfStockPortOver['Average Cost'] = dfStockPortOver['Book Cost']/dfStockPortOver['Quantity']
            self.dfStockPortRecords = df.sort_values(by='Date', ascending = False).head(10)
            self.dfStockPortOver = dfStockPortOver.sort_values(by = "Book Cost", ascending = False)

        def returnTable(self, choice:str)->pd.DataFrame:
            match choice:
                case 'Overview':
                    return self.dfStockPortOver
                case 'records':
                    return self.dfStockPortRecords
                case _:
                    return None

        def returnBookCost(self)->str:
           return str(round(self.dfStockPortOver['Book Cost'].sum(),2))

def main():
        PortFolio = Portfolio("data/data.csv")
        
        dfDis = PortFolio.returnTable('Overview')

        # Create table
        money = dash_table.FormatTemplate.money(2)
        columns = [
                dict(id = 'Symbol', name = 'Symbol'),
                dict(id = 'Quantity', name = 'Quantity'),
                dict(id = 'Book Cost', name = 'Book Cost', type = 'numeric', format = money),
                dict(id = 'Average Cost', name = 'Average Cost', type = 'numeric', format = money),
                ]

        # Initialize the App
        app = Dash(__name__, external_stylesheets = [dbc.themes.ZEPHYR])

        # Create the app layout
        app.layout = [
                    html.Div(children = html.H2(
                        children = "Stock Portfolio"),
                        id = 'Header'
                        ),
                    
                    html.Div(
                    children = [
                        html.Div(
                            children = [
                                        html.Div(
                                            children = [
                                                html.H3(children = 'Book Cost' , id = "BookCostTitle"),
                                                html.Div(
                                                    children = [
                                                        str(round(dfDis['Book Cost'].sum().tolist(),2)) + ' USD'
                                                        ],
                                                        id = 'BookCost_Value'
                                                    )
                                            ]
                                            ),
                                        ],
                            id = 'Portfolo',
                            className = 'flex-child'
                        ),
                        html.Div(
                            children = [
                                dcc.RadioItems(
                                        options = ['Book Cost', 'Quantity'],
                                        value = 'Book Cost',
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
                            dash_table.DataTable(columns = columns, 
                             data=dfDis.to_dict('records'), 
                             page_size = 10,
                             sort_action = 'native',
                            filter_action = 'native', id = "PortSum")],

                            id = "PortOverview"
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
