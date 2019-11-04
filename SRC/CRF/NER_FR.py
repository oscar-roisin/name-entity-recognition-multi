import subprocess
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

filename="model/crf_fr.pickle"

file = open(filename, 'rb')
crf = pickle.load(file)
file.close()

print("Loaded: "+filename)

sent = ""
while True:
    print()
    sent = input("Give a sentence in French (q to exit): ")
    # sent = 'Je m'appelle Ken et je viens de Paris.'
    if sent in ['q']:
        break

    file1= open("fr.tmp","w")
    file1.write(sent)
    file1.flush()
    file1.close()

    batcmd = "../fr-tag/cmd/tree-tagger-french"

    result = subprocess.check_output([batcmd, 'fr.tmp'])
    
    words = []
    posTags = []
    i=0
    for word in result.split():
        word=word.decode("utf-8")
        if i % 3 == 0:
            words.append(word)
        if i % 3 == 1:
            if len(word.split(":"))>1:
                posTags.append(word.split(':')[0])
            else:
                posTags.append(word)
        i = i + 1

    data=[]
    for i in range(len(words)):
        word = words[i]
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