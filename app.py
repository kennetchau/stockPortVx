from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

# Reading the csv
df = pd.read_csv("data/data.csv")
df['Book Cost'] = df['Quantity'] * df['Cost']

# Create a work df 
dfWork = df.drop('Cost', axis = 1)

# Create Table to display
dfDis = df.groupby(by=['Symbol']).sum()
dfDis = dfDis[['Quantity','Book Cost']]
dfDis['Average Cost'] = dfDis['Book Cost']/dfDis['Quantity']
dfDis = dfDis.reset_index().sort_values(by = "Book Cost")

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
                                html.Div(
                                        children = [
                                        html.H3(children = "Portfolio Overview", id = 'PortSum_Title'),
                                        dash_table.DataTable(columns = columns, 
                                         data=dfDis.to_dict('records'), 
                                         page_size = 10,
                                         sort_action = 'native',
                                        filter_action = 'native', id = "PortSum")]
                                    )
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

if __name__ == '__main__':
    app.run(debug = True)
