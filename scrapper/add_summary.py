import pandas as pd
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
from vcgz.web_dashboard.utils import download_database

from transformers import pipeline
from tqdm import tqdm

import nltk
import pymongo 
import urllib
tqdm.pandas()



def cut_into_chunk(text_with_punctuation,pipe_summarizer_nlp, max_len_sentence=1024):
    sentences = nltk.tokenize.sent_tokenize(text_with_punctuation)
    # initialize
    length = 0
    chunk = ""
    chunks = []
    count = -1
    for sentence in sentences:
        count += 1
        combined_length = len(pipe_summarizer_nlp.tokenizer.tokenize(sentence)) + length # add the no. of sentence tokens to the length counter
        if combined_length  <= max_len_sentence: # if it doesn't exceed
            chunk += sentence + " " # add the sentence to the chunk
            length = combined_length # update the length counter
            # if it is the last sentence
            if count == len(sentences) - 1:
                chunks.append(chunk) # save the chunk
        else: 
            chunks.append(chunk) # save the chunk
            # reset 
            length = 0 
            chunk = ""
            # take care of the overflow sentence
            chunk += sentence + " "
            length = len(pipe_summarizer_nlp.tokenizer.tokenize(sentence))
    return chunks


def update_field_on_filter(myclient,database,collection,filter_to_select,field,value, print_df=False):
    mydb = myclient[database]
    mycol = mydb[collection]
    newvalues = { "$set": { field: value} }
    result = mycol.update_many(filter_to_select, newvalues)
    if print_df:
        print('Matched count: ' + str(result.matched_count))
        print('Modified count: ' + str(result.modified_count))


def generate_summary(all_chunks,nb_by_chunks=1, with_device = True):
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]
    all_summary = []
    for chunk in chunks(all_chunks,nb_by_chunks):
        print('Chunk')
        inputs = pipe_summarizer_2.tokenizer.batch_encode_plus(chunk, return_tensors="pt", max_length=1024, padding='max_length', truncation=True)
        if with_device:
            inputs = inputs.to(0)
        outputs = pipe_summarizer_2.model.generate(inputs['input_ids'])
        all_summary = all_summary  + pipe_summarizer_2.tokenizer.batch_decode(outputs, skip_special_tokens=True) 
    return '\n\n'.join(all_summary)


pipe_summarizer_2 = pipeline("summarization",'plguillou/t5-base-fr-sum-cnndm')
password="HASI0KjXi@hk1uTUV&9T8u6q0C52VqD2h?c#goH0"
client= pymongo.MongoClient(f"mongodb+srv://vcgz_admin:"+urllib.parse.quote(password)+"@veilleconcurentielle.zfgil.mongodb.net/vcdataout?retryWrites=true&w=majority")
df = download_database(client,'recorded_video','video_subtitles',list_of_field = ['subtitle','video_id','subtitle_with_punct','summary'],
                         filter = { "subtitle_with_punct": { "$exists": True },"summary": { "$exists": False } })

df['chunks'] =  df['subtitle_with_punct'].progress_apply(cut_into_chunk,pipe_summarizer_nlp = pipe_summarizer_2, max_len_sentence=1024)
for i in tqdm(range(len(df))):
    summary = generate_summary(df.chunks.iloc[i],with_device=False)
    update_field_on_filter(client,'recorded_video','video_subtitles',{'video_id':df.video_id.iloc[i]},'summary',summary, print_df=True)                                                                                                                                    