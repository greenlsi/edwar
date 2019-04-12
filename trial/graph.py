import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
# import pandas as pd
# import time
import os


def printGraph(df1, df2, df3):
    server = flask.Flask('app')
    server.secret_key = os.environ.get('secret_key', 'secret')

    # df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/hello-world-stock.csv')

    app = dash.Dash('app', server=server)

    app.scripts.config.serve_locally = False
    dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'
    colors = {
    'background': '#111111',
    'text': '#7FDBFF'
    }

    app.layout = html.Div([
        html.H1(
            'Empatica',
            style={
                'textAlign': 'center',
                'color': '#2D74BA'
            }),
        dcc.Dropdown(
            id='my-dropdown',
            options=[
                {'label': 'EDA', 'value': 'EDA'},
                {'label': 'HR', 'value': 'HR'},
                {'label': 'TEMP', 'value': 'TEMP'}
            ],
            value='EDA',
            style={
                'textAlign': 'left',
            }
        ),
        dcc.Graph(
            id='my-graph'
            ),

    ],
    className="container",
    style={
        # 'backgroundColor': colors['background'],
        'marginBottom': 0, 'marginTop': 0,
        'marginLeft':0, 'marginRight':0
    })

    @app.callback(Output('my-graph', 'figure'),
                  [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        # dff = df[df['Stock'] == selected_dropdown_value]
        if selected_dropdown_value == 'EDA':
            dff = df1
            units = 'μS'
        elif selected_dropdown_value == 'HR':
            dff = df2
            units = 'bpm'
        elif selected_dropdown_value == 'TEMP':
            dff = df3
            units = 'ºC'
        else:
            dff = None
            units = '?'

        return {
            'data': [{
                # 'x': (dff[2:].index-2)/(dff.medida[1]*3600),
                'x': dff.index,
                'y': dff.medida,
                'line': {
                    'width': 3,
                    'shape': 'spline'
                }
            }],
            'layout': {
                'xaxis': {
                'title': 'hours'},
                'yaxis': {'title': units},
                'margin': {
                    'l': 30,
                    'r': 20,
                    'b': 30,
                    't': 20
                },
                'plot_bgcolor': '#FFFFFF',
                'paper_bgcolor': '#FFFFFF',
                'font': {
                    'color': '#000000'
                }
            }
        }

    # if __name__ == '__main__':
    app.run_server()

# Checking Code
# df1 = pd.read_csv('EDA.csv', header=None)
# df2 = pd.read_csv('HR.csv', header=None)
# df3 = pd.read_csv('TEMP.csv', header=None)
# df1.columns=['medida']
# df2.columns=['medida']
# df3.columns=['medida']
# printGrapgh(df1, df2, df3)
