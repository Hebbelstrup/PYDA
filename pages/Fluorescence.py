import base64
import io
import dash
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from scipy import optimize
import numpy as np
from sklearn.metrics import r2_score
from dash.dependencies import ALL

pd.options.mode.chained_assignment = None  # Fixes slice error in pandas dataframe

config = {'toImageButtonOptions': {
    'format': 'svg'
}}


def parse_content(contents):  # Takes in one element from "upload-Data","contents" and returns a dataframe for that file

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    file = io.StringIO(decoded.decode('utf-8'))

    df = pd.read_csv(file, sep="\n|\\t", decimal='.', names=["nM", "I"], engine='python', header=None)
    df = pd.DataFrame(df)
    data_start = float(df.loc[df['nM'].str.startswith('#DATA')].index[0] + 1)
    data = df[int(data_start):]
    data['nM'] = data['nM'].astype(float)

    return data


def fit_unfolding(x, Fn, An, Fd, Ad, m, U):
    return (Fn + An * x) + ((Fd + Ad * x) * np.exp((m * (x - U)) / (0.59))) / (1 + np.exp((m * (x - U)) / 0.59))


def fit_binding(x,PC,Kd,y0,yf):
    return y0+((yf-y0)/(2*PC)) * (PC+x+Kd) - np.sqrt(((PC+x+Kd)**2)-(4*PC*x))


dash.register_page(__name__, title='fluorescence')

layout = html.Div(id='parent', children=[
    html.H1(id='H1', children='Fluorescence Plotter',
            style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
    html.Div(children=
             ['A plotter for fluorescence data from Perkin Elmer LS50B spectrofluorometers', html.Br(),
              'Uploading more than one file will overlay them']
             , style={'textAlign': 'center', 'marginBottom': 20}),
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

    html.Button('concentration', id='fluoro_concentrations', n_clicks=0,
                style={
                    'display': 'none'
                }),
    html.Button('Fitting', id='fitting_button', n_clicks=0,
                style={
                    'display': 'none'
                }),

    dbc.Tabs([]
             , id="fluoro_tabs",
             active_tab='normal',
             style={'display': 'none'},
             ),

    dcc.Graph(id='Fluorescence_plot', config=config),
    html.Div(id='slider_container',
             children=[dcc.Slider(id='wavelength_slider', min=0, max=10, step=1, value=5,
                                  marks={0: f'{0}', 10: f'{10}'},
                                  tooltip={'placement': 'bottom', 'always_visible': True})],
             style={'display': 'none'}),

    html.P(id='Fluorescence_placeholder'),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Concentrations"), className="mx-auto"),
            dbc.ModalBody(children="No files uploaded?", id='modalbody'),
            dbc.ModalFooter(
                dbc.Button(
                    "Close & save", id="close", className="mx-auto", n_clicks=0
                )
            ),
        ],
        id="modal",
        is_open=False,
    ),

    dcc.Store(id='concentrations_store'),
    dcc.Store(id='fit_parameters_store'),
    dcc.Store(id='nm_slider_store'),
    html.Div(id='tester'),

    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Fitting"), className="mx-auto"),
            dbc.ModalBody(children=[
                html.Div([
                    html.H5('Fill in all initial parameter guesses for either binding or unfolding before clicking "Close & Save"',style={'textAlign':'center'}),
                    html.H2('Unfolding', style={'textAlign': 'center', 'margin-left': 50}),
                    html.H5('Fn: ',
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='Fn_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H5('An: ',
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='An_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H5('Fd: ',
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='Fd_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H5('Ad: ',
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='Ad_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H5('m: ',
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='m_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H5(['D',html.Sub('50%'),': '],
                            style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='U_guess', type='number', placeholder='initial guess',
                              style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.Br(),
                    html.H2(' '),
                    html.H2('Binding', style={'textAlign': 'center', 'margin-left': 50}),
                    html.H5('Protein',style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30,'width': '100px'}),
                    dcc.Input(id='protein_concentration', type='number', placeholder='µM',style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.H5('Kd',style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.Input(id='Kd_guess', type='number', placeholder='Initial guess',style={'display': 'inline-block', 'border': '1px solid black'}),
                    html.H5('fitting mode',style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}),
                    dcc.RadioItems(id='fitting_mode',options=['Unfolding','Binding'],inline=True,value='Unfolding',style={'display': 'inline-block'})


                ], style={'display': 'inline-block'})]),

            dbc.ModalFooter(
                dbc.Button(
                    "Close & save", id="fit_close", className="mx-auto", n_clicks=0
                )
            ),
        ],
        id='fit_modal',
        is_open=False,
    )
])


@callback(Output('modalbody', 'children'),
          # Only updates when new files are upoaded. Not when button is clicked. Very usefull for the storage of Inputs
          [Input('upload-data', 'contents'), Input('upload-data', 'filename')], config_prevent_initial_callbacks=True)
def update_modal_with_files(content, filename):  # Renders the layout for the modal.

    names = [html.H4(i, id=f'{i}_name',
                     style={'display': 'inline-block', 'margin-left': 30, 'margin-right': 30, 'width': '100px'}) for i
             in filename]
    input = [dcc.Input(id={'type': 'component', 'index': i}, type='number', placeholder='concentration',
                       style={'display': 'inline-block', 'border': '1px solid black'}) for i in filename]
    together = []
    for i in range(0,
                   len(names)):  # Has to be done this way to such that its just one large list. Lists of list !does not work!
        together.append(names[i])
        together.append(input[i])
    return html.Div(together)


@callback(Output('modal', 'is_open'), Output("close", 'n_clicks'), Output('concentrations_store', 'data'),
          [Input('fluoro_concentrations', 'n_clicks'), Input("close", 'n_clicks'),
           State({'type': 'component', 'index': ALL}, 'value')], config_prevent_initial_callbacks=True)
# This call back takes outputs the concentrations that is inputtet, and saves it in concentrations_store, as a list. The order of the concentrations follow the order of filenames. ie. zip(concentrations_store,filename)
# gives correct concentrations for each files

def create_concentrations(open_clicks, close_clicks, concentrations):
    if open_clicks >= 1 and close_clicks == 0:

        return True, 0, concentrations


    else:  # Can only happen when close_clicks >= 1. gets set to zero in both open and close.
        return False, 0, concentrations


@callback(Output('fit_modal', 'is_open'), Output('fit_close', 'n_clicks'), Output('fit_parameters_store', 'data'),
          [Input('fitting_button', 'n_clicks'), Input('fit_close', 'n_clicks'),
           Input('Fn_guess', 'value'), Input('An_guess', 'value'), Input('Fd_guess', 'value'),
           Input('Ad_guess', 'value'),
           Input('m_guess', 'value'), Input('U_guess', 'value'),Input('protein_concentration','value'),Input('Kd_guess','value'),Input('fitting_mode','value')])

def open_fitting(open_clicks, close_clicks, Fn, An, Fd, Ad, m, U,PC,Kd,fitting_mode):
    if open_clicks >= 1 and close_clicks == 0:

        return True, 0, [[Fn, An, Fd, Ad, m, U],[PC,Kd],fitting_mode]

    else:  # Can only happen when close_clicks >= 1. gets set to zero in both open and close.
        return False, 0, [[Fn, An, Fd, Ad, m, U],[PC,Kd],fitting_mode]


@callback(Output('fluoro_concentrations', 'style'),
          # Input is whenever files are uploaded. Output is style and className for the button
          Output('fluoro_concentrations', 'className'),
          Output('fitting_button', 'style'),
          Output('fitting_button', 'className'),
          Input('upload-data', 'contents'), config_prevent_initial_callbacks=True)
def update_button(
        data):  # Returns style and position for button if more than 1 file is uploaded. Button is used for concentration input.
    if len(data) > 1:
        style = {'width': '154px', 'height': '30px', 'marginTop': 5}
        position = "d-grid gap-2 col-6 mx-auto"

        return style, position, style, position

    else:
        return {'display': 'none'}, None


@callback(Output('fluoro_tabs', 'children'),
          Output('fluoro_tabs', 'style'),
          Output('fluoro_tabs', 'className'),
          Input('upload-data', 'contents'), config_prevent_initial_callbacks=True)
def update_tab(event):
    return [
               dbc.Tab(label='Normal', tab_id='normal'),
               dbc.Tab(label='Wavelength', tab_id='wavelength'),
               dbc.Tab(label='Intensity', tab_id='intensity')
           ], None, 'mx-auto'


@callback(Output('Fluorescence_plot', 'figure'),
          Output('nm_slider_store', 'data'),
          Output('slider_container', 'style'),
          [Input('upload-data', 'contents'),
           Input('fluoro_tabs', 'active_tab'),
           Input('concentrations_store', 'data'),
           Input('wavelength_slider', 'value'),
           Input('fit_close', 'n_clicks'),
           Input('fit_parameters_store', 'data')
           ], config_prevent_initial_callbacks=True)
def plot_fluorescence(content, active_tab, concentrations, slider_value, fit_close_clicks, fit_parameters):
    data = [parse_content(i) for i in content]
    fig = make_subplots(rows=1, cols=1)

    style = {'display': 'none'}
    I_max = data[0][
        'I'].max()  # Messy, but need to define values for slider outside of choice of tab, because changing tab initiates the update of the slider values
    slider_initial_nm = data[0].loc[data[0]['I'] == float(I_max)]['nM']
    slider_min = data[0]['nM'].min()
    slider_max = data[0]['nM'].max()

    try:
        if len(concentrations) == len(data) and None not in concentrations:
            pass
        else:
            concentrations = [i for i in range(0, len(data))]
    except:
        concentrations = [i for i in range(0, len(data))]

    if active_tab == 'normal':
        for i in range(0, len(data)):
            fig.add_trace(go.Scatter(x=data[i]['nM'], y=data[i]['I'], name=concentrations[i]), row=1, col=1)

        fig['layout']['xaxis']['title'] = 'λ<sub>(nm)</sub>'
        fig['layout']['yaxis']['title'] = 'I'

    ### WAVELENGTH PLOTTER. CURRENTLY TAKES THE NM WITH MAX INT FOR FILE 0 AND PLOTS FOR ALL

    if active_tab == 'wavelength':

        nm = slider_value
        y = []
        for i in range(0, len(data)):
            I_at_nM = float(data[i].loc[data[i]['nM'] == nm]['I'])
            y.append(I_at_nM)
        fig.add_trace(go.Scatter(x=concentrations, y=y, name='Data', mode='markers'), row=1, col=1)
        fig['layout']['xaxis']['title'] = 'Concentration'
        fig['layout']['yaxis']['title'] = f'I<sub>{nm} nm</sub>'

        style = {'display': 'block', 'transform': 'scale(1)'}

        sorted_data = list(zip(concentrations, y))
        sorted_data = sorted(sorted_data, key=lambda tup: tup[0])
        sorted_x, sorted_y = zip(*sorted_data)


        if fit_parameters[1] and None not in fit_parameters[1] and fit_parameters[2] == 'Binding':
            try:

                custom = lambda sorted_x, Kd,y0,yf: fit_binding(sorted_x,fit_parameters[1][0],Kd,y0,yf)
                par,pcov = optimize.curve_fit(custom, sorted_x, sorted_y, p0=[np.array(fit_parameters[1][1]),int(np.min(sorted_y)),int(np.max(sorted_y))])
                perr = np.sqrt(np.diag(pcov))
                y_pred = custom(np.array(sorted_x),*par)
                r2 = r2_score(sorted_y,y_pred)
                fig.add_trace(
                    go.Scatter(x=np.array(sorted_x), y=y_pred, mode='lines', line={'width':1,'dash':'dash'},
                               name=f'Kd = {par[0]:.3} +- {perr[0]:.3} µM\
                               <br>yf = {par[2]:.3} +- {perr[2]:.3} µM\
                               <br>R<sup>2</sup> = {r2:.3}')

                )


            except Exception as e:
                print(e)


        if fit_parameters[0] and None not in fit_parameters[0] and fit_parameters[2] == 'Unfolding':

            try:

                par, pcov = optimize.curve_fit(fit_unfolding, sorted_x, sorted_y, p0=fit_parameters[0])
                perr = np.sqrt(np.diag(pcov))
                y_pred = fit_unfolding(np.array(sorted_x), *par)

                r2 = r2_score(sorted_y, y_pred)

                fig.add_trace(
                    go.Scatter(x=np.array(sorted_x), y=y_pred, mode='lines',
                               line={'width': 1, 'dash': 'dash'},
                               name=f'Fn = {par[0]:.3} +- {perr[0]:.3}\
                                    <br>An = {par[1]:.3} +- {perr[1]:.3}\
                                    <br>Fd = {par[2]:.3} +- {perr[2]:.3}\
                                    <br>Ad = {par[3]:.3} +- {perr[3]:.3}\
                                    <br>m = {par[4]:.3} +- {perr[4]:.3} Kcal*mol<sup>-1</sup>*M<sup>-1</sup>\
                                    <br>D<sub>50%</sub> = {par[5]:.3} +- {perr[5]:.3}\
                                    <br>R<sup>2</sup> = {r2:.3}')

                )

            except Exception as e:
                print(e)

    if active_tab == 'intensity':

        y = []
        for i in range(0, len(data)):
            I_max = data[i]['I'].max()
            nm_at_int = data[i].loc[data[i]['I'] == float(I_max)]['nM']
            y.append(float(nm_at_int))

        fig.add_trace(go.Scatter(x=concentrations, y=y, mode='markers', name='data'), row=1, col=1)

        fig['layout']['xaxis']['title'] = 'Concentration'
        fig['layout']['yaxis']['title'] = 'λmax<sub>(nm)</sub>'

        ### START OF FITTING
        sorted_data = list(zip(concentrations, y))
        sorted_data = sorted(sorted_data, key=lambda tup: tup[0])
        sorted_x, sorted_y = zip(*sorted_data)

        if fit_parameters[1] and None not in fit_parameters[1] and fit_parameters[2] == 'Binding':
            try:

                custom = lambda sorted_x, Kd, y0, yf: fit_binding(sorted_x, fit_parameters[1][0], Kd, y0, yf)
                par, pcov = optimize.curve_fit(custom, sorted_x, sorted_y,p0=[np.array(fit_parameters[1][1]), int(np.min(sorted_y)),int(np.max(sorted_y))])
                perr = np.sqrt(np.diag(pcov))
                y_pred = custom(np.array(sorted_x), *par)
                r2 = r2_score(sorted_y, y_pred)
                fig.add_trace(
                    go.Scatter(x=np.array(sorted_x), y=y_pred, mode='lines', line={'width': 1, 'dash': 'dash'},
                               name=f'Kd = {par[0]:.3} +- {perr[0]:.3} µM\
                                <br>yf = {par[2]:.3} +- {perr[2]:.3} µM\
                                <br>R<sup>2</sup> = {r2:.3}')
                )

            except Exception as e:
                print(e)


        if fit_parameters[0] and None not in fit_parameters[0] and fit_parameters[2] == 'Unfolding':

            try:

                par, pcov = optimize.curve_fit(fit_unfolding, sorted_x, sorted_y, p0=fit_parameters[0])
                perr = np.sqrt(np.diag(pcov))
                y_pred = fit_unfolding(np.array(sorted_x), *par)

                r2 = r2_score(sorted_y, y_pred)

                fig.add_trace(
                    go.Scatter(x=np.array(sorted_x), y=y_pred, mode='lines',
                               line={'width': 1, 'dash': 'dash'},
                               name=f'Fn = {par[0]:.3} +- {perr[0]:.3}\
                                    <br>An = {par[1]:.3} +- {perr[1]:.3}\
                                    <br>Fd = {par[2]:.3} +- {perr[2]:.3}\
                                    <br>Ad = {par[3]:.3} +- {perr[3]:.3}\
                                    <br>m = {par[4]:.3} +- {perr[4]:.3} Kcal*mol<sup>-1</sup>*M<sup>-1</sup>\
                                    <br>D<sub>50%</sub> = {par[5]:.3} +- {perr[5]:.3}\
                                    <br>R<sup>2</sup> = {r2:.3}')
                )



            except Exception as e:
                print(e)

    return fig, [slider_min, slider_max, slider_initial_nm], style


@callback(Output('slider_container', 'children'),
          Input('fluoro_tabs', 'active_tab'),
          State('nm_slider_store', 'data'),
          config_prevent_initial_callbacks=True)
def updateslider(content, slider_data):
    if slider_data:
        minimum = slider_data[0]
        maximum = slider_data[1]
        nm_at_int_max = slider_data[2][0]

        slider = ['Use slider to change what wavelength to follow',
                  dcc.Slider(id='wavelength_slider',
                             min=minimum, max=maximum, step=1, value=nm_at_int_max,
                             marks={int(minimum): f'{minimum}', int(maximum): f'{int(maximum)}'},
                             tooltip={'placement': 'bottom', 'always_visible': True}),
                  ]


    else:
        pass

    return slider
