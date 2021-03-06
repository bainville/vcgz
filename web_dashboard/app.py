import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output
from utils import *
import yaml

from datetime import datetime
import pandas as pd
pd.options.plotting.backend = "plotly"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


df = pd.DataFrame()
df_intro = pd.DataFrame()
all_subjects_df = pd.DataFrame.from_dict(all_subjects,orient='index').T

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Link(html.Button('Accueil'), href='/'),
    dcc.Link(html.Button('Tendances'), href='/topics'),
    dcc.Link(html.Button('Résumé'), href='/summary'),
    html.H1(children="Analyse des tendances de la présidentielle", style = {'textAlign': 'center'}),
    html.P(id= 'time'),
    html.P(id='onload'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])


introduction_layout = html.Div([   
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


summary_layout =  html.Div(
    children = [   

        html.Div([dcc.Dropdown(
            id='dropdown_candidat',
            options=[{'label': 'Melenchon', 'value': 'Melenchon'},
                {'label': 'Macron', 'value': 'Macron'},
                {'label': 'Zemmour', 'value': 'Zemmour'},
                {'label': 'Le Pen', 'value': 'LePen'},
                {'label': 'Pecresse', 'value': 'Pecresse'}
                ])],
            className="six columns"),
        html.Div([dcc.Dropdown(
            id='dropdown_video',
            options=[]
                )],
            className="six columns"),
        html.Br(),
        html.Br(),
        html.Div(id='result_summary')
])



# Update the index
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/topics':
        return topics_layout
    elif pathname == '/summary':
        return summary_layout
    else:
        return introduction_layout


@app.callback(Output('time', 'children'),
              Input('onload','children'))
def update_data(a):
    print('Dernière mise à jour: ' + str(datetime.now()))
    global df_intro
    df_intro = prepare_intro_data()
    global df
    df = prepare_topics_data()
    last_date = last_date_of_video()
    return [html.Div(['Dernière mise à jour du back: ' + datetime.now().strftime('%H:%M %d-%m-%Y') ,html.Br(), 'Date de la dernière vidéo: '+last_date])]


@app.callback(Output('intro_table','children'),
              Input('onload','children'))
def introduction_two_tables(n):
    def make_clickable(val):
        return "<a href='{0}' target='_blank'>{0}</a>".format(val)
    with open('input.yaml', 'r') as stream:
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


@app.callback(Output('dropdown_list', 'options'),
              Input('tabs_groupby', 'value'))
def topics_update_dropdown_options(tab):
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
def topics_create_fig(value,tab):
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
                html.P("(La dernière valeur peut être partiel puisque la dernière semaine peut ne pas être fini)", style = {'textAlign': 'center','font-style': 'italic'})
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
                html.P("(La dernière valeur peut être partiel puisque la dernière semaine peut ne pas être fini)", style = {'textAlign': 'center','font-style': 'italic'})
                            ])
        return res_layout, None, topics_word_layout
 

@app.callback(Output('dropdown_video', 'options'),
              Input('dropdown_candidat', 'value'))
def summary_update_dropdown_options(value_candidat):
    df = download_database(client,'recorded_video','video_subtitles',list_of_field = ['title','video_id'],filter={'personality_name':value_candidat})
    df = df.iloc[::-1]
    res = [{'label':df.title.iloc[i],'value':df.video_id.iloc[i] } for i in range(len(df))]
    return res


@app.callback(Output('result_summary', 'children'),
              Input('dropdown_video', 'value'))
def summary_return_text(video_id):
    df = download_database(client,'recorded_video','video_subtitles',list_of_field = ['subtitle_with_punct','summary'],filter={'video_id':video_id})
    res = html.Div([
        html.H3(children="Résumé", style = {'textAlign': 'center'}),
        html.Div(html.P(df.summary.iloc[0], style = { 'width': '980px',
                                                      'height': '490px'}),
                                            style = {'textAlign': 'justify',
                                                        "background-color": "#F8B2A2",
                                                        'border': '1px black solid',
                                                        "margin-left": "auto",
                                                        "margin-right": "auto",
                                                        'font-style': 'italic',
                                                        'width': '1000px',
                                                        'height': '200px',
                                                        'overflow': 'auto'}),
        html.Br(),
        html.H3(children="Sous titres de la vidéo", style = {'textAlign': 'center'}),
        html.Div(html.P(df.subtitle_with_punct.iloc[0].replace('\n','<br>'), style = { 'width': '980px',
                                                                    'height': '490px'}),
                                                        style = {'textAlign': 'justify',
                                                                    "background-color": "#F9856B",
                                                                    'border': '1px black solid',
                                                                    "margin-left": "auto",
                                                                    "margin-right": "auto",
                                                                    'font-style': 'italic',
                                                                    'width': '1000px',
                                                                    'height': '500px',
                                                                    'overflow': 'auto'})
        ])
    return res


if __name__ == "__main__":
    app.run_server(debug=True)
