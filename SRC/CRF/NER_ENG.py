import pickle
import pandas as pd
import nltk
import utils
from utils import *

SENT_COL="sent"
TOKEN_COL="token"
SHAPE_COL="token_shape"
POS_COL="pos"
NER_COL="ner"

filename="model/crf_eng.pickle"

file = open(filename, 'rb')
crf = pickle.load(file)
file.close()

print("Loaded " + filename )

sent = ""
while True:
    print()
    sent = input("Give a sentence in English (q to exit): ")
    #     sent = "Adam could jump from England to Washington."
    if sent in ['q']:
        break
    tokenized_sent = nltk.word_tokenize(sent)

    pos_tagged_tokens = nltk.pos_tag(tokenized_sent)
    tokens=[]
    posTags=[]

    for token,pos_tag in pos_tagged_tokens:
        tokens.append(token)
        pos = pos_tag
        posTags.append(pos)
    
    data=[]
    for i in range(len(tokens)):
        word = tokens[i]
        pos = posTags[i]
        ner = "unknown"
        data.append([1,word,pos,ner])

    df = pd.DataFrame(data, columns = [ SENT_COL, TOKEN_COL, POS_COL, NER_COL ]) 


    analyseTokens(df)

    getter_sent = SentenceGetter(df)
    pred_sentence = getter_sent.sentences

    X_sent = [sent2features(s) for s in pred_sentence]
    y_pred = crf.predict(X_sent)[0]

    df[NER_COL]=y_pred
    df = df.drop([SENT_COL,SHAPE_COL], axis=1)

    df.rename(columns={TOKEN_COL:TOKEN_COL.upper(),POS_COL:POS_COL.upper(),NER_COL:NER_COL.upper()}, 
                     inplace=True)
    print("\n")
    print(df)
print("\nWhat would it mean if you got to quit?")