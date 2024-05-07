import base64
import io
import dash
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy import optimize
from sklearn.metrics import r2_score
from dash import dcc,callback
from dash import html
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

dash.register_page(__name__, title='CD')

config = {'toImageButtonOptions': {
    'format':'svg'
}}

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    file = io.StringIO(decoded.decode('utf-8'))

    data = pd.read_csv(file, sep="\n|\\t", names=['λ', 'Elip', 'Sat'], decimal=',', engine="python")
    if data['Elip'].isna().any():

        num_rows = len(data['Elip'])
        data['Sat'] = [0] * num_rows
    print(data)

    df = pd.DataFrame(data)
    df = df[20:df.loc[df['λ'].str.startswith('#####')].index[0]].astype('float')
    df = df.loc[(df['Sat'] <= 700)]

    return df


def Denature(x, An, Bn, Ad, Bd, dS, dH):  # Function to be fitted to data
    return (An + Bn * (x + 273) + (Ad + Bd * (x + 273)) * np.exp((dS * (x + 273) - dH) / (0.00831 * (x + 273)))) / (
                1 + np.exp((dS * (x + 273) - dH) / (0.00831 * (x + 273))))


layout = html.Div(id='parent', children=[
    html.H1(id='H1', children='CD Plotter', style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
    html.Div(children=
                ['A plotter for data from JASCO CD systems',html.Br(), 'Uploading more than one file will overlay them ',html.Br(),
                 'Uploading file containing temperature data will allow for fitting of denaturation']
                              ,style={'textAlign':'center','marginBottom':20}),
    dcc.Upload(id="upload-data", children=html.Div([html.A("Select File(s)")]),
               style={
                   "width": "305px",
                   # "height": "60px",
                   # "lineHeight": "60px",
                   "borderWidth": "1px",
                   "borderStyle": "solid",
                   "borderRadius": "5px",
                   "textAlign": "center",
                   # "margin": "5px",
               },
               multiple=True,
               className="d-grid gap-2 col-6 mx-auto"),
    dcc.Input(id='Concentration', value=None, type='number', placeholder='Concentration in µM',className="d-grid gap-2 col-2 mx-auto"),
    dcc.Input(id='Peptide-bonds', value=None, type='number', placeholder='Peptide bonds',className="d-grid gap-2 col-2 mx-auto"),
    dcc.Checklist(id='Converter', options=[{'label': 'Convert to MRE', 'value': 'Convert'}],className="d-grid gap-2 col-2 mx-auto",
                  style={'display': 'inline-block'}),
    dcc.Checklist(id="checklist", inline=True),

    dcc.Graph(id='line_plot',config=config),

    html.P(id='Initial_guess_note',style={'display':'none'},children='Fill in all initial parameter guesses, then click "fit data"'),
    dcc.Input(id='An', style={'display': 'none'}, type='number', placeholder='Initial An'),
    dcc.Input(id='Bn', style={'display': 'none'}, type='number', placeholder='Initial Bn'),
    dcc.Input(id='Ad', style={'display': 'none'}, type='number', placeholder='Initial Ad'),
    dcc.Input(id='Bd', style={'display': 'none'}, type='number', placeholder='Initial Bd'),
    dcc.Input(id='dS', style={'display': 'none'}, type='number', placeholder='Initial ΔS'),
    dcc.Input(id='dH', style={'display': 'none'}, type='number', placeholder='Initial ΔH'),

    html.Button('Fit data', id='fit', n_clicks=0, style={'display': 'none'}),

    html.P(id='Fit_messages', style={'display': 'inline-block'}),

    html.P(id='placeholder'),

    ])


@callback(Output('placeholder', 'children'), [Input('Concentration', 'value'), Input('Peptide-bonds', 'value')], )
def update_output(concentration, peptide_bonds):
    global conversion
    try:
        conversion = (10 * (concentration / 1000000) * 0.1 * peptide_bonds)
    except:
        conversion = 1


@callback(Output('line_plot', 'figure'),
              Output('fit', 'n_clicks'),
              Output('Fit_messages', 'children'),
              [State('upload-data', 'contents'),
               State('upload-data', 'filename'),
               Input('Converter', 'value'),
               Input('Concentration', 'value'),
               Input('Peptide-bonds', 'value'),
               Input('checklist', 'value'),
               Input('fit', 'n_clicks'),
               State('An', 'value'),
               State('Bn', 'value'),
               State('Ad', 'value'),
               State('Bd', 'value'),
               State('dS', 'value'),
               State('dH', 'value')], prevent_initial_call=True)
def plot_data(contents, filename, convert, C, P, files, clicks, An, Bn, Ad, Bd, dS, dH):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']
    fig = make_subplots(rows=2, cols=1, row_heights=[0.8, 0.2])
    i = 0
    message = None
    for data, filename in zip(contents, filename):
        if f'{filename}' in files:
            df = parse_contents(data, filename)

            if convert:
                x = df['λ']
                y = df['Elip'].div(conversion)

            else:
                x = df['λ']
                y = df['Elip']

            fig.add_trace(go.Scatter(x=x, y=y, line={'width': 4, 'color': colors[i]}, name=filename), row=1, col=1)
            fig.add_trace(go.Scatter(x=x, y=df['Sat'], line={'width': 1, 'color': colors[i]}, showlegend=False), row=2,
                          col=1)
            i += 1

            if clicks:
                try:
                    par, pcov = optimize.curve_fit(Denature, x.to_numpy(), y.to_numpy(), p0=[An, Bn, Ad, Bd, dS, dH])
                    perr = np.sqrt(np.diag(pcov))
                    y_pred = Denature(x.to_numpy(), *par)
                    r2 = r2_score(y.to_numpy(), y_pred)

                    fig.add_trace(
                        go.Scatter(x=x, y=Denature(x.to_numpy(), par[0], par[1], par[2], par[3], par[4], par[5]),
                                   line={'width': 1, 'color': colors[i], 'dash': 'dash'},
                                   name=f'An = {par[0]:.3} +- {perr[0]:.3}\
                                                                                             <br>Bn = {par[1]:.3} +- {perr[1]:.3}\
                                                                                             <br>Ad = {par[2]:.3} +- {perr[2]:.3}\
                                                                                             <br>Bd = {par[3]:.3} +- {perr[3]:.3}\
                                                                                             <br>ΔS = {par[4]:.3} +- {perr[4]:.3} J*K<sup>-1</sup>mol<sup>-1</sup>\
                                                                                             <br>ΔH = {par[5]:.3} +- {perr[5]:.3} Kj*mol<sup>-1</sup>\
                                                                                             <br>R<sup>2</sup> = {r2:.3}\
                                                                                             <br>T<sub>m</sub> = {par[5] / par[4] - 273:.3} °C')
                        , row=1, col=1)
                except Exception as e:
                    message = f'There was an error: {e}'

            else:
                pass

            if x.max() <= 100 and convert:
                fig['layout']['xaxis2']['title'] = '°C'
                fig['layout']['yaxis1']['title'] = "θ<sub>MRE</sub>*10<sup>-3</sup>(deg*cm<sup>2</sup>dmol<sup>-1</sup>"



            elif x.max() <= 100 and not convert:
                fig['layout']['xaxis2']['title'] = '°C'
                fig['layout']['yaxis1']['title'] = 'θ'

            elif x.max() >= 100 and convert:
                fig['layout']['xaxis2']['title'] = 'λ<sub>(nm)</sup>'
                fig['layout']['yaxis1']['title'] = "θ<sub>MRE</sub>*10<sup>-3</sup>(deg*cm<sup>2</sup>dmol<sup>-1</sup>"
                fig.add_hline(y=0, row=1, col=1,line_dash="dash")

            elif x.max() >= 100 and not convert:
                fig['layout']['xaxis2']['title'] = 'λ<sub>(nm)</sup>'
                fig['layout']['yaxis1']['title'] = 'θ'
                fig.add_hline(y=0, row=1, col=1,line_dash="dash")
            else:
                pass  # Pass on x / y labels. Incase something goes wrong
        else:
            pass  # Pass on if no matches between selected files and filenames

    fig['layout']['yaxis2']['title'] = 'HT Voltage'  # Update all axis with this
    if (df['Sat'] == 0).any():
        fig['layout']['yaxis2']['title'] = 'No HT available'
    fig.update_layout(showlegend=True)
    return [fig, None, message]


@callback(
    Output("checklist", "options"),
    Output("checklist", "value"),
    [Input("upload-data", "filename")], prevent_initial_call=True)
def update_file_select(filenames):
    return [[i for i in filenames], [i for i in
                                     filenames]]  # returns first for options and then for values. its the same in this case. This type of callback needs [[],[]] - List of lists.


###### START OF FITTING #######

@callback(Output('An', 'style'), Output('Bn', 'style'), Output('Ad', 'style'), Output('Bd', 'style'),
              Output('dS', 'style'), Output('dH', 'style'), Output('fit', 'style'), Output('Initial_guess_note','style'),
              [Input('checklist', 'value')], prevent_initial_call=True)
def show_fit_parameters(selected_files):
    if len(selected_files) > 1:
        return [{'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'},
                {'display': 'none'}]
    else:

        return [{'display': 'block'},
                {'display': 'block'},
                {'display': 'block'},
                {'display': 'block'},
                {'display': 'block'},
                {'display': 'block'},
                {'width': '154px', 'height': '30px', 'marginTop': 5},
                {'display': 'block'}]



