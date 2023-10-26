import base64
import io
import dash
from dash import html, dcc, callback, Input, Output, dash_table,State
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import numpy as np

dash.register_page(__name__, title='akta')

config = {'toImageButtonOptions': {
    'format':'svg'

}}

def get_xy(name,df):
    x_loc = df.columns.get_loc(name) -1
    x = df.iloc[:,x_loc]
    y = df[name]
    name = name
    return x,y,name

def parse_content(contents):


    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    file = io.StringIO(decoded.decode('utf-8'))
    df = pd.read_csv(file, delimiter="\n|\\t", decimal=".", header=2, engine='python')
    df = pd.DataFrame(df)

    if len(np.where(df['mAU'].isnull())[0]) != 0:

        mAU_NaN = np.where(df['mAU'].isnull())[0]

        shift = df.columns.get_loc('mAU') - 1


        df[mAU_NaN.min():] = df[mAU_NaN.min():].shift(shift,axis=1)


    return df

layout = html.Div(id='parent', children=[
            html.H1(id='H1', children='Äkta Plotter', style={'textAlign': 'center', 'marginTop': 40, 'marginBottom': 40}),
            html.Div(children=
                ['A plotter for data from Äkta systems',html.Br(), 'Uploading more than one file will only overlay 280 nm']
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
                           # "margin": "5px",
                       },
                       multiple=True,
                       className="d-grid gap-2 col-6 mx-auto"),
            dcc.Graph(id='akta_plot',config=config),
            html.H1(id='output-data-upload'),
            html.P(id='placeholder'),



])






@callback(Output('akta_plot','figure'),
          Output('output-data-upload','children'),
          [Input('upload-data','contents'),
           State('upload-data','filename')],config_prevent_initial_callbacks=True)


def plot_data(contents,filename):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = px.colors.qualitative.Plotly

    if len(contents) == 1:
        for data in contents:
            df = parse_content(data)
           # df2 = df[96:]
           # df = df[0:96]

        for k,i in enumerate(df.columns[1::2]): # every other column is the "event". The column before is the mL of that event.
            x,y,name = get_xy(i,df) # this returns the ml and the event in a data frame.
            if name =='mAU':
                fig.add_trace(go.Scatter(x=x,y=y,name=name,line=dict(color=colors[k])),secondary_y=False)
            #    fig.add_trace(go.Scatter(x=df2['ml'][96:], y=df2['Fraction'][96:], name=name, line=dict(color=colors[k]),showlegend=False), secondary_y=False)

            if name not in ['Fraction','Logbook','Injection','mAU']:
                fig.add_trace(go.Scatter(x=x, y=y, name=name,visible='legendonly',line=dict(color=colors[k])), secondary_y=True)
            if name == 'Logbook' :
                pass
            if name == 'Fraction':

                fig.add_trace(go.Scatter(x=[0, 0], y=[0, 0], mode='lines',
                                         legendgroup='Fractions', name='fractions',visible='legendonly'))
                for k,i in enumerate(x.dropna()):

                    fig.add_trace(go.Scatter(x=[i,i],y=[df['mAU'].astype(float).min(),df['mAU'].astype(float).max()/15],
                                             mode='lines',
                                             legendgroup='Fractions',name='fractions',showlegend=False,
                                             opacity=0.5,line=dict(color='black'),visible='legendonly'))
                    fig.add_trace(go.Scatter(x=[i], y=[df['mAU'].astype(float).max()/15],mode='text',text=k+1, orientation='v',
                                            textposition="top center",showlegend=False,legendgroup='Fractions',visible='legendonly'))
                                                                    # adds numbers to fraction lines.
                                                                    # Needs to be done like this because
                                                                    # of the x=[i,i] adds to points
                                                                    # so numbering will be dublicates
        fig['layout']['xaxis']['title'] = 'ml'
        fig['layout']['yaxis1']['title'] = '280 nm'
        return fig, None

    else:
        for data,filename in zip(contents,filename):
            df = parse_content(data)

            fig.add_trace(go.Scatter(x=df['ml'],y=df['mAU'],name=filename))

        fig['layout']['xaxis']['title'] = 'ml'
        fig['layout']['yaxis1']['title'] = '280 nm'
        return fig,None


