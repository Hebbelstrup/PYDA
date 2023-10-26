import base64
import io
import dash
from dash import html, dcc, callback, Input, Output,State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash.dependencies import ALL



def parse_content(contents): # Takes in one element from "upload-Data","contents" and returns a dataframe for that file


    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    file = io.StringIO(decoded.decode('utf-8'))

    df = pd.read_csv(file, sep=" ", names=['m/z','I'])
    df = pd.DataFrame(df)

    return df


dash.register_page(__name__, title='Mass Spectrometry')

config = {'toImageButtonOptions': {
    'format':'svg'
}}

layout = html.Div(id='MS_parent', children=[
            html.H1(id='MS_description', children='Mass spec Plotter', style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
            html.Div(children=
                ['A plotter for Mass Spec data from the Agilent system',html.Br(), 'Uploading more than one file will overlay them']
                              ,style={'textAlign':'center','marginBottom':20}),
            dcc.Upload(id='upload-data', children=html.Div([html.A("Select File(s)")]),
                       style={
                           "width": "305px",
                           # "height": "60px",
                           # "lineHeight": "60px",
                           "borderWidth": "1px",
                           "borderStyle": "solid",
                           "borderRadius": "5px",
                           "textAlign": "center",
                           "marginBottom": "5px",
                       },
                       multiple=True,
                       className="d-grid gap-2 col-6 mx-auto"),
            dcc.Graph(id='MS_plot',config=config),

])


@callback(Output('MS_plot','figure'),
          [Input('upload-data','contents'),
          Input('upload-data','filename')],config_prevent_initial_callbacks=True)

def ms_plotting(content,filename):

    data = [parse_content(i) for i in content]
    fig = make_subplots(rows=1,cols=1)
    for i,k in zip(data,filename):

        y = (i['I'].div(i['I'].max())) * 100
        x = i['m/z']

        fig.add_trace(go.Scatter(x=x,y=y,name=k))

    fig['layout']['xaxis']['title'] = 'm/z'
    fig['layout']['yaxis']['title'] = '%'

    return fig

