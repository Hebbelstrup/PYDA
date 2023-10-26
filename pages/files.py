import dash
from dash import Dash, dcc, html, Input, Output,callback
import dash_bootstrap_components as dbc

dash.register_page(__name__,title='Files')



layout = html.Div(children=[

    html.H1(children='Files'
            ,style={'textAlign':'center'}),

    html.Div(children=
        ['A libary of files used in creating the scripts',html.Br(),
        'Use them either to test the plotters or to ensure your data has the same format'],

            style={'textAlign':'center'}),
    html.Div(children=
    [
        dbc.Button(
            "CD Far UV",
            href="assets/Data/CD_FarUv.txt",
            download="CD_FarUV",
            external_link=True,
            color="dark",
            outline=True
        ),
        dbc.Button(
            "CD temperature denaturation",
            href="assets/Data/CD_temp.txt",
            download="CD_temperature",
            external_link=True,
            color="dark",
            outline=True
        ),
        dbc.Button(
            "Fluorescence",
            href="assets/Data/Fluorescence.sp",
            download="Fluorescence",
            external_link=True,
            color="dark",
            outline=True
        ),
         dbc.Button(
             "ÄKTA",
             href="assets/Data/Akta.txt",
             download="ÄKTA",
             external_link=True,
             color="dark",
             outline=True,
         ),

    ],
    className="d-grid gap-2 col-6 mx-auto")]
)
