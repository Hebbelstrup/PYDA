import dash
import numpy as np
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
from dash.dependencies import ALL

dash.register_page(__name__, title='bootstrapper')

layout = html.Div(id='bootstrapper_intro', children=[
            html.H1('Bootstrapper', style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
            html.Div(['A bootstrapper to simulate the error of multiple fits'], style={'textAlign':'center','marginBottom':20}),
            dcc.Dropdown(id='boot_dropper',
                         options=[{'label':i,'value':i} for i in np.arange(1,11,1)],
                         multi=False,
                         placeholder='Number of fits',
                         style={'width':200,'margin':'auto'},

                         ),
            html.Div(id='bootstrapper_input', children='',className="d-grid col-2 mx-auto"
                     ,style={'textAlign':'center','marginTop':10,'marginBottom':10}),
            dbc.Button('Fit the values',id='bootstrap_button',className='d-grid col-4 mx-auto',style={'textAlign':'center','marginTop':10,'marginBottom':10},n_clicks=0),
            html.H1(id='bootstrap_result',children=[],className='d-grid col-4 mx-auto',style={'textAlign':'center'}),
        ])


@callback(Output('bootstrapper_input','children'),
          Input('boot_dropper','value'),config_prevent_initial_callbacks=True)

def update_number_of_fits(boot_dropper_value):
    if boot_dropper_value != None:

        Value = [dcc.Input(id={'type':'Value','index':i},type='number',placeholder='Enter value here',style={'textAlign':'center'}) for i in range(1,boot_dropper_value+1)]
        Error = [dcc.Input(id={'type':'Error','index':i},type='number',placeholder='Error',style={'textAlign':'center','width':'60px'}) for i in range(1,boot_dropper_value+1)]

        together = []

        for i in range(0,len(Value)):
            together.append(Value[i])
            together.append(Error[i])



        return html.Div(together)

    else:
        pass

@callback(Output('bootstrap_result','children'),
          [Input('bootstrap_button','n_clicks'),State({'type':'Value','index':ALL},'value'),State({'type':'Error','index':ALL},'value')],config_prevent_initial_callbacks=True)

def calculate_bootstrap(n_clicks,values,errors):
    try:
        iterations = 1000
        Gaussians = [np.random.normal(x,y,1000) for x,y in zip(values,errors)] # Creates a Gaussian distributions for each data and error pair. Saved in list

        bootstrap = []
        for i in range(0, iterations):
            averages = []
            for x in range(0, len(values)):  # Loop to go through each value in values
                mean_gaussian = np.mean([Gaussians[x][k] for k in np.random.randint(0, 1000,3)])
                                                                                                 # Picks a random index in Gaussians[x] between 0 and 1000, three times. Then takes the mean of those three

                averages.append(mean_gaussian)  # Adds mean of Gaussians values to list
            bootstrap.append(np.mean(averages))  # Adds the mean of the first iteration to a list. This list will then hold iterations amount of numbers.
        return f'{np.mean(bootstrap):.3f} +- {np.std(bootstrap):.3f}'

    except:
        return ['Error!',html.Br(),'Did you fill in all values?']





