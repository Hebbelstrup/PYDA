import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
dash.register_page(__name__,title='Home')

tool_tip_text = "This Dashboard is designed to be used with data generated in the course 'Protein science'. \n" \
                "Examples of accepted files and formats can be found under 'files'. \n" \
                "More information on fits can be found in \n " \
                "Lindorff-Larsen, K & Teilum, K 'Linking thermodynamics and measurements of protein stability, 2021' "
layout = html.Div(children=[

        dbc.Tooltip(tool_tip_text,
                     target="question-mark-icon"),
        html.Div(
        [
            html.Img(id="question-mark-icon", src="https://img.icons8.com/material/48/000000/help.png"),
        ],
        style={"display": "inline-block"}
        ),


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