import dash
from dash import html, dcc

dash.register_page(__name__,title='Home')

layout = html.Div(children=[
    html.H1(children='Welcome to PYDA',
            style={'textAlign':'center','marginTop':'20px'}),

    html.Div(children=[
        "A dashboard developed for the course Protein Science" , html.Br(), 'Different scripts can be accessed with the dropdown menu'
    ],style={'textAlign':'center'}),

    html.Div(children='''
        By Alexander Hebbelstrup.
    ''', style={'textAlign':'center'},
        className="fixed-bottom bg-dark text-white"),


])