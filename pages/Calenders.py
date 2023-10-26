import dash
from dash import html

dash.register_page(__name__, title='Calenders')

layout = html.Div(children=[html.H1('Overview of calenders for SBiNLab',style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 20}),
                            html.Iframe(
                                src='https://teamup.com/ks2c34d39bb683096a',
                                style={'border':'O','width':'1850px','height':'800px'},className="d-grid gap-2 col-6 mx-auto"),
                            html.Iframe(
                                src='https://teamup.com/ksk3sa262qd9msry66',
                                style={'border': 'O', 'width': '900px', 'height': '600px','margin':26}),
                            html.Iframe(
                                src='https://teamup.com/ksiam57om3ixp4tjwr',
                                style={'border': 'O', 'width': '900px', 'height': '600px','margin':26},
                                )



]),



