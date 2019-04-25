import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import time
import os


def printGraph(df):
    server = flask.Flask('app')
    server.secret_key = os.environ.get('secret_key', 'secret')
    dates = sorted(df.keys())
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
        dcc.RadioItems(
            id='my-radioitems',
            options=[{'label': i[10:12]+'/'+i[8:10]+'/'+i[4:8], 'value': i} for i in dates],
            value=dates[0],
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id='graph-1')
    ],
    className="container",
    style={
        # 'backgroundColor': colors['background'],
        'marginBottom': 0, 'marginTop': 0,
        'marginLeft':0, 'marginRight':0
    })

    @app.callback(Output('graph-1', 'figure'),
                  [Input('my-dropdown', 'value'),
                  Input('my-radioitems', 'value')
                  ])

    def update_graph_1(selected_dropdown_value, selected_radioitem_value):
        # dff = df[df['Stock'] == selected_dropdown_value]
        if (selected_dropdown_value == 'EDA'):
            dff = df.get(selected_radioitem_value)[0]
            units = 'μS'
        elif (selected_dropdown_value == 'HR'):
            dff = df.get(selected_radioitem_value)[1]
            units = 'bpm'
        elif (selected_dropdown_value == 'TEMP'):
            dff = df.get(selected_radioitem_value)[2]
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
                # 'xaxis': {
                # 'title': 'hours'},
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

#Checking Code
# df1 = pd.read_csv('/home/juanfdez/codigo/empatica/MG4118012/basals/raw_20181008/Dataexport/EDA.csv', header=None)
# df2 = pd.read_csv('/home/juanfdez/codigo/empatica/MG4118012/basals/raw_20181008/Dataexport/HR.csv', header=None)
# df3 = pd.read_csv('/home/juanfdez/codigo/empatica/MG4118012/basals/raw_20181008/Dataexport/TEMP.csv', header=None)
# df1.columns=['medida']
# df2.columns=['medida']
# df3.columns=['medida']
# printGraph(df1, df2, df3)
