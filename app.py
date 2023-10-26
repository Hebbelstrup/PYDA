from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc
from assets.navbar import create_navbar
from dash import html, dcc, callback, Input, Output, State


app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LUX])

nav = create_navbar()
server = app.server


app.layout = html.Div([
    html.Div([nav]),
    dash.page_container,
])



if __name__ == '__main__':
	app.run_server(debug=True)