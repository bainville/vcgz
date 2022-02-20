import json
import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output
from utils import *
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import random

#fig = px.line(x=df_by_subject.europe.resample('W').sum().rolling(3).apply(z_score).index, y=df_by_subject.europe.resample('W').sum().rolling(3).apply(z_score), title="sample figure", height=325)

app = dash.Dash(__name__)
app.layout = html.Div(
    children = [
    
    html.H1(children="Analyse des tendances de la présidentielle", style = {'textAlign': 'center'}),
    
    dcc.Tabs(id="tabs_groupby", value='by_candidates', children=[
        dcc.Tab(label='By candidates', value='by_candidates'),
        dcc.Tab(label='By topics', value='by_topics'),
    ]),   
    dcc.Dropdown(
            id='my-dropdown',
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

df = prepare_data()
all_subjects_df = pd.DataFrame.from_dict(all_subjects,orient='index').T


@app.callback(output=dash.dependencies.Output('my-dropdown', 'options'),
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
        
@app.callback([Output('result_graph', 'children'),
               Output("loading-output", "children"),
               Output('result_table', 'children')],
               [Input('my-dropdown', 'value'),
               Input('tabs_groupby', 'value')]
)
def send_fig(value,tab):
    if value is None:
        return None, None, None
    if tab == 'by_candidates':
        df_to_plot = df.xs(value,level=1,axis=1).dropna(how='all')
        df_to_plot.columns.name = 'Topics'

        fig = df_to_plot.plot(kind='bar',
                              labels={"value":"Nombre d'occurence","upload_date":"Semaine"},
                              text_auto='.2s')
        fig.update_layout(barmode = "relative") #stack #relative #overlay #group
        fig.update_traces(patch={"visible":'legendonly'})

        return html.Div([
                html.H3(value.title(), style = {'textAlign': 'center'}),
                dcc.Graph(id="graph-1-tabs",
                          figure=fig,
                          style={
                                'height': 700,
                                'width': 1000,
                                "display": "block",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                })
            ]), None, html.Div([html.H3('Mots par topics', style = {'textAlign': 'center'}),
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
                                                    }]
    ,) ])
    elif tab == 'by_topics':
        df_to_plot = df.xs(value,level=0,axis=1).dropna(how="all")
        df_to_plot.columns.name = 'Candidat'

        fig = df_to_plot.plot(kind='bar',
                              labels={"value":"Nombre d'occurence","upload_date":"Semaine"},
                              text_auto='.2s')
        fig.update_layout(barmode = "relative") #stack #relative #overlay #group
        fig.update_traces(patch={"visible":'legendonly'})

        return html.Div([
                html.H3(value.title(), style = {'textAlign': 'center'}),
                dcc.Graph(id="graph-1-tabs",
                          figure=fig,
                          style={
                                'height': 700,
                                'width': 1000,
                                "display": "block",
                                "margin-left": "auto",
                                "margin-right": "auto",
                                })
            ]), None, html.Div([html.H3('Mots par topics', style = {'textAlign': 'center'}),
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
                                                    }]
                                                    ,) ])
 

if __name__ == "__main__":
    app.run_server(debug=False)
