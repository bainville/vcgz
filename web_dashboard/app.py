import json
import dash
from dash import dcc
from dash import html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.express as px
import random


#fig = px.line(x=df_by_subject.europe.resample('W').sum().rolling(3).apply(z_score).index, y=df_by_subject.europe.resample('W').sum().rolling(3).apply(z_score), title="sample figure", height=325)

all_subjects = {}
all_subjects['démocratie'] = ['constituante', 'référendum','révolution citoyenne','révolutions','vote obligatoire','électorale','réforme','groupe parlementaire']
all_subjects['education'] = ['enseignement professionnel','enseignement','apprentissage','acquis','lire','écrire','compter']
all_subjects['justice'] = ['justice','impunité','greffier','magistrat','peines planchers','place de prison','majorité pénale','multirécidiviste']
all_subjects['economie'] = ['dette','milieux populaires','précarité','protectionnisme','lutte travailleurs','retraite']
all_subjects['agriculture'] = ['élévage','élevage intensif']
all_subjects['ecologie'] = ['mer','écologie','environement']
all_subjects['outre_mer'] = ['outre mer', 'antilles','guadeloupéens','martiniquais','eau potable','assainissement','chlordécone','haïti','calédonie','territoires insulaires',
 'caraïbes']
all_subjects['ruralité'] = [ 'campagnes','monde rural']
all_subjects['europe'] = ['parlement européen','europe','éuropéene']
all_subjects['immigration'] = ['immigration', 'immigrés','nationalité','expulser']
all_subjects['identité'] = ['islam','créolisation', 'quartiers populaires','fachos','musulmans','quartiers','civilisation','culture', 'être français','racisme','francophonie','française']
all_subjects['sécurité']= ['crime','délit','délinquance','prison']
all_subjects['lutte_contre_la_fraude'] = ['paradis fiscaux','évasion fiscale','fiscale','fraude sociale']
all_subjects['santé'] = ['dose','gestes barrières','soignants','tests gratuits','couvre feu','confinement','pandémie','ars','ephad','maison de retraite']
all_subjects['international'] = ['ukraine','russie','venezuela','états unis','pékin', 'chine', 'taïwan', 'russes']

def prepare_data_by_people(people):
    df = pd.read_excel("C:/Users/isaac/Documents/vcgz/web_dashboard/All_Corpus_Punct_" + people + ".xlsx",index_col=0)
    df_by_subject = df.set_index('upload_date')[['Text_of_punctuation']]
    for key in all_subjects.keys():
        df_by_subject[key] = df_by_subject.Text_of_punctuation.apply(lambda win:sum([str(win).lower().count(i) for i in all_subjects[key]]))
    df_to_plot = df_by_subject.resample('W-SAT').sum()
    df_to_plot.columns = [i.title() for i in df_to_plot.columns ]
    df_to_plot.columns.name='Topics'
    return df_to_plot


def prepare_data():
    print('We are loading data')
    res = {}
    for people in ['Melenchon','Macron','Zemmour','LePen']:
        df_to_plot = prepare_data_by_people(people)
        res[people]  = df_to_plot
    all_res = pd.concat(res,axis=1)
    return all_res


app = dash.Dash(__name__)
df = prepare_data()
all_subjects_df = pd.DataFrame.from_dict(all_subjects,orient='index').T

app.layout = html.Div(
    children = [
    
    html.H1(children="Analyse des tendances de la présidentielle", style = {'textAlign': 'center'}),
    
    dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
        dcc.Tab(label='By candidates', value='tab-1-example-graph'),
        dcc.Tab(label='By topics', value='tab-2-example-graph'),
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
    html.Div(id='tabs-content-example-graph'),
    html.Div(id='tabs-content-example-table')
])


@app.callback(output=dash.dependencies.Output('my-dropdown', 'options'),
              inputs=[Input('tabs-example-graph', 'value')])
def change_my_dropdown_options(tab):
    if tab == 'tab-1-example-graph':
        return [{'label': 'Melenchon', 'value': 'Melenchon'},
                {'label': 'Macron', 'value': 'Macron'},
                {'label': 'Zemmour', 'value': 'Zemmour'},
                {'label': 'Le Pen', 'value': 'LePen'},
                {'label': 'Pecresse', 'value': 'Pecresse'}]
    elif tab == 'tab-2-example-graph':
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
        
@app.callback(
    [Output('tabs-content-example-graph', 'children'),Output("loading-output", "children"),Output('tabs-content-example-table', 'children')],
    [Input('my-dropdown', 'value'),Input('tabs-example-graph', 'value')]
)
def read_excel_and_send_fig(value,tab):
    if value is None:
        return None, None, None
    if tab == 'tab-1-example-graph':
        df_to_plot = df.xs(value,level=0,axis=1)

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
    elif tab == 'tab-2-example-graph':
        df_to_plot = df.xs(value.title(),level=1,axis=1)

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
    app.run_server(debug=True)
