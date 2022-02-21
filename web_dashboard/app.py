import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output
from utils import *
import yaml

from datetime import datetime
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import random
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.DataFrame()
df_intro = pd.DataFrame()
all_subjects_df = pd.DataFrame.from_dict(all_subjects,orient='index').T

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
app.layout = html.Div([
    dcc.Link(html.Button('Accueil'), href='/'),
    dcc.Link(html.Button('Tendances'), href='/topics'),
    html.H1(children="Analyse des tendances de la présidentielle", style = {'textAlign': 'center'}),
    html.P(id= 'time'),
    dcc.Interval(id='interval-component',interval= 5*3600*1000, n_intervals=0, disabled=False),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])


index_layout = html.Div([   
    html.Br(),
    html.P(children= 'Voici un récapitulatif de toutes les vidéos suivis', style = {'textAlign': 'center'}),
    html.Div(
             id = 'intro_table',
             style={'width': '96%','padding-left':'2%', 'padding-right':'2%'})
])


topics_layout = html.Div(
    children = [
    html.H3(children="Tendances", style = {'textAlign': 'center'}),
    
    dcc.Tabs(id="tabs_groupby", value='by_candidates', children=[
        dcc.Tab(label='By candidates', value='by_candidates'),
        dcc.Tab(label='By topics', value='by_topics'),
    ]),   
    dcc.Dropdown(
            id='dropdown_list',
            options=[]
        ),
    dcc.Loading(
                id="loading",
                children=[html.Div([html.Div(id="loading-output")])],
                type="default",
            ),
    html.Div(id='result_graph'),
    html.Div(id='result_table')
    
])


# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/topics':
        return topics_layout
    else:
        return index_layout


@app.callback([Output('time', 'children')],
              Input('interval-component', 'n_intervals'))
def update_data(n):
    print('Dernière mise à jour: ' + str(datetime.now()))
    print(n)
    global df_intro
    df_intro = prepare_intro_data()
    global df
    df = prepare_topics_data()
    last_date = last_date_of_video()
    return [html.Div(['Dernière mise à jour du back: ' + datetime.now().strftime('%H:%M %d-%m-%Y') ,html.Br(), 'Date de la dernière vidéo: '+last_date])]


@app.callback(output=Output('dropdown_list', 'options'),
              inputs=[Input('tabs_groupby', 'value')])
def change_my_dropdown_options(tab):
    if tab == 'by_candidates':
        return [{'label': 'Melenchon', 'value': 'Melenchon'},
                {'label': 'Macron', 'value': 'Macron'},
                {'label': 'Zemmour', 'value': 'Zemmour'},
                {'label': 'Le Pen', 'value': 'LePen'},
                {'label': 'Pecresse', 'value': 'Pecresse'}]
    elif tab == 'by_topics':
         return [{'label': 'Démocratie', 'value': 'démocratie'},
                {'label': 'Education', 'value': 'education'},
                {'label': 'Justice', 'value': 'justice'},
                {'label': 'Economie', 'value': 'economie'},
                {'label': 'Agriculture', 'value': 'agriculture'},
                {'label': 'Ecologie', 'value': 'ecologie'},
                {'label': 'Outre mer', 'value': 'outre_mer'},
                {'label': 'Ruralité', 'value': 'ruralité'},
                {'label': 'Europe', 'value': 'europe'},
                {'label': 'Immigration', 'value': 'immigration'},
                {'label': 'Identité', 'value': 'identité'},
                {'label': 'Sécurité', 'value': 'sécurité'},
                {'label': 'Lutte contre la fraude', 'value': 'lutte_contre_la_fraude'},
                {'label': 'Santé', 'value': 'santé'},
                {'label': 'International', 'value': 'international'}]


@app.callback([Output('result_graph', 'children'),Output("loading-output", "children"),Output('result_table', 'children')],
               [Input('dropdown_list', 'value'),Input('tabs_groupby', 'value')])
def send_fig(value,tab):
    topics_word_layout = html.Div([html.H3('Mots par topics', style = {'textAlign': 'center'}),
                dash_table.DataTable(data = all_subjects_df.to_dict(orient='records'),
                         columns =  [{"id": str(i) ,'name':i.replace('_',' ').title() } for i in all_subjects_df.columns],
                         id='tbl',
                         style_cell={'textAlign': 'center',
                                     'whiteSpace': 'normal',
                                     'height': 'auto'},
                         style_table={'overflowX': 'auto'},
                         style_header={
                                       'backgroundColor': '#F35330',
                                       'fontWeight': 'bold',
                                       'border': '2px solid green'
                                      },
                         style_data_conditional=[{
                                                'if': {'row_index': 'odd'},
                                                'backgroundColor': 'rgb(220, 220, 220)',
                                                    }])
                                    ])
    if value is None:
        return None, None, None
    if tab == 'by_candidates':
        df_to_plot = df.xs(value,level=1,axis=1).dropna(how='all')
        df_to_plot.columns.name = 'Topics'

        fig = df_to_plot.plot(kind='bar',
                              labels={"value":"Nombre d'occurence","upload_date":"Semaine (début)"},
                              text_auto='.2s')
        fig.update_layout(barmode = "relative") #stack #relative #overlay #group
        res_layout = html.Div([
                html.H3(value.title(), style = {'textAlign': 'center'}),
                dcc.Graph(id="graph-1-tabs",
                          figure=fig,
                          style={
                                'height': 700,
                                'width': 1000,
                                "display": "block",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                }),
                html.P("(La dernière valeur peut être partiel puisque la semaine n'est pas fini)", style = {'textAlign': 'center','font-style': 'italic'})
            ])
        return res_layout, None, topics_word_layout
    elif tab == 'by_topics':
        df_to_plot = df.xs(value,level=0,axis=1).dropna(how="all")
        df_to_plot.columns.name = 'Candidat'

        fig = df_to_plot.plot(kind='bar',
                              labels={"value":"Nombre d'occurence","upload_date":"Semaine (début)"},
                              text_auto='.2s')
        fig.update_layout(barmode = "relative") #stack #relative #overlay #group
        #fig.update_traces(patch={"visible":'legendonly'})
        res_layout = html.Div([
                html.H3(value.title(), style = {'textAlign': 'center'}),
                dcc.Graph(id="graph-1-tabs",
                          figure=fig,
                          style={
                                'height': 700,
                                'width': 1000,
                                "display": "block",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                }),
                html.P("(La dernière valeur peut être partiel puisque la semaine n'est pas fini)", style = {'textAlign': 'center','font-style': 'italic'})
                            ])
        return res_layout, None, topics_word_layout
 


@app.callback(Output('intro_table','children'),
              Input('interval-component', 'n_intervals'))
def send_intro_table(n):
    def make_clickable(val):
        return "<a href='{0}' target='_blank'>{0}</a>".format(val)
    with open('C:/Users/isaac/Documents/vcgz/scrapper/input.yaml', 'r') as stream:
        input_data = pd.DataFrame(yaml.safe_load(stream),index=['Link']).T.reset_index()
    input_data['Link'] = input_data['Link'].apply(make_clickable)
    input_data.columns = ['Candidat','Lien']
    table_input = html.Div([dash_table.DataTable(data = input_data.to_dict(orient='records'),
                                    columns =  [{"id": i ,'name':i, "presentation": "markdown"} for i in input_data.columns],
                                    id='table_input',
                                    style_cell={'textAlign': 'center',
                                                'whiteSpace': 'normal',
                                                'width': '10%',
                                                'overflow': 'hidden',
                                                'textOverflow': 'ellipsis'},
                                    style_table={'overflowX': 'auto',
                                                  'width': '90%'},
                                    style_header={'backgroundColor': '#F35330',
                                                  'fontWeight': 'bold',
                                                  'border': '2px solid green'},
                                    style_data_conditional=[{'if': {'row_index': 'odd'},
                                                            'backgroundColor': 'rgb(220, 220, 220)'}],
                                    markdown_options={"html": True})
                            ],className="six columns")

    table_intro = html.Div([dash_table.DataTable(data = df_intro.to_dict(orient='records'),
                                    columns =  [{"id": i ,'name':i} for i in df_intro.columns],
                                    id='table_intro',
                                    style_cell={'textAlign': 'center',
                                                'whiteSpace': 'normal',
                                                'width': '10%',
                                                'overflow': 'hidden',
                                                'textOverflow': 'ellipsis'},
                                    style_table={'overflowX': 'auto',
                                                  'width': '90%'},
                                    style_header={'backgroundColor': '#F35330',
                                                  'fontWeight': 'bold',
                                                  'border': '2px solid green'},
                                    style_data_conditional=[{'if': {'row_index': 'odd'},
                                                            'backgroundColor': 'rgb(220, 220, 220)'}])
                            ], className="six columns") 

    res_html = html.Div(children = [table_input,table_intro])

    return res_html


if __name__ == "__main__":
    app.run_server(debug=True)
