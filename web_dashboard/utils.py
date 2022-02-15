import pymongo 
import urllib
import pandas as pd


password="HASI0KjXi@hk1uTUV&9T8u6q0C52VqD2h?c#goH0"
client= pymongo.MongoClient(f"mongodb+srv://vcgz_admin:"+urllib.parse.quote(password)+"@veilleconcurentielle.zfgil.mongodb.net/vcdataout?retryWrites=true&w=majority")

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

def download_database_specific_field(myclient, name_of_database, name_of_collection, list_of_field, with_id=False, filter={}):
    dict_of_field = {i: 1 for i in list_of_field}
    if with_id:
        dict_of_field['_id'] = 1
    else:
        dict_of_field['_id'] = 0
    mydb = myclient[name_of_database]
    collection = mydb[name_of_collection]
    df_temp = pd.DataFrame(list(collection.find(filter, dict_of_field)))
    return df_temp

def prepare_data():
    print('We are loading data')
    df = download_database_specific_field(client,'recorded_video','video_subtitles',['subtitle','upload_date','personality_name'])
    df['upload_date'] = pd.to_datetime(df['upload_date'],format='%Y%m%d')
    df = df.set_index('upload_date')

    for key in all_subjects.keys():
        df[key] = df.subtitle.apply(lambda win:sum([str(win).lower().count(i) for i in all_subjects[key]]))
    df = df.drop('subtitle',axis=1).reset_index()
    df_resultats = df.pivot_table(values=df.columns[1:],index='upload_date',columns=['personality_name'])
    df_resultats = df_resultats.mask(df_resultats==0).resample('W-SAT').sum(min_count=1)
    print('Data is ready!')
    return df_resultats