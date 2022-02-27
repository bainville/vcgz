import pandas as pd
from transformers import pipeline
from tqdm import tqdm
from vcgz.web_dashboard.utils import download_database
import pymongo 
import urllib
import re
from collections import OrderedDict
tqdm.pandas()



def update_field_on_filter(myclient,database,collection,filter_to_select,field,value, print_df=False):
    mydb = myclient[database]
    mycol = mydb[collection]
    newvalues = { "$set": { field: value} }
    result = mycol.update_many(filter_to_select, newvalues)
    if print_df:
        print('Matched count: ' + str(result.matched_count))
        print('Modified count: ' + str(result.modified_count))


def treat_text(text, pipe_restore_punct=None):
    text = text.replace('*', '').replace('&nbsp;', '').replace('  ', ' ').replace('&lt;i&gt;', '')
    text = re.sub('\\[[^\\[\\]]*\\]', '', text)
    if len(text) > 0:
        count_of_punct = (text.count('.') + text.count('!') + text.count('?')) / len(text)
    else:
        count_of_punct = 0.1
    if count_of_punct > 0.005:
        all_text_with_punct = text
    else:
        sentences = add_punctuation(text, pipe=pipe_restore_punct)
        all_text_with_punct = ' '.join(sentences)
    return all_text_with_punct


def add_punctuation(text_init, pipe=None):

    def cut_sentences(text, positions_to_cut, add_last=False):
        sentences = []
        positions_to_cut.insert(0, 0)
        for i in range(1, len(positions_to_cut)):
            if not positions_to_cut[i] == 0:
                if positions_to_cut[i] == 1:
                    pass
                else:
                    sentences.append(text[positions_to_cut[(i - 1)]:positions_to_cut[i]])
            if add_last:
                sentences.append(text[positions_to_cut[(-1)]:])
            sentences = [s.strip() for s in sentences]
            sentences = [s[0].title() + s[1:] for s in sentences if s != '']
            sentences = [(s.replace(' !', '!') + '.').replace('..', '.').replace('!.', '!') for s in sentences]
        return sentences

    start_position = 0
    sentences = []
    cond = True
    compt = 0
    while cond:
        print(compt)
        text = text_init[start_position:start_position + 2500]
        if text == '':
            break
        result = pipe([text])[0]
        result = pd.DataFrame(result)
        try:
            list_of_cut = result.start.loc[(result.word.str.contains('[!.?]', regex=True) == False)].to_list()
        except AttributeError:
            print('we are here')
            print(text)
            cond=False
            list_of_cut = [len(text)]
        else:
            list_of_cut = list(OrderedDict.fromkeys(list_of_cut))
            if len(text) < 2500:
                cond = False
            sentences += cut_sentences(text, list_of_cut, add_last=(cond == False))
            start_position = start_position + list_of_cut[(-1)]
        compt = compt+1
    return sentences


password="HASI0KjXi@hk1uTUV&9T8u6q0C52VqD2h?c#goH0"
client= pymongo.MongoClient(f"mongodb+srv://vcgz_admin:"+urllib.parse.quote(password)+"@veilleconcurentielle.zfgil.mongodb.net/vcdataout?retryWrites=true&w=majority")
df = download_database(client,'recorded_video','video_subtitles',list_of_field = ['subtitle','video_id'], filter = { "subtitle_with_punct": { "$exists": False } })
pipe_restore_punct = pipeline("token-classification", "cfinley/punct_restore_fr")

for i in tqdm(range(len(df))):
    summary = treat_text(df.subtitle.iloc[i],pipe_restore_punct)
    update_field_on_filter(client,'recorded_video','video_subtitles',{'video_id':df.video_id.iloc[i]},'subtitle_with_punct',summary, print_df=True)