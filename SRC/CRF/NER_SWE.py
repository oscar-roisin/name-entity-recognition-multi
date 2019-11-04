import pickle
import pandas as pd
import RDRPOS
from RDRPOS import *
import nltk
import utils
from utils import *

SENT_COL="sent"
TOKEN_COL="token"
SHAPE_COL="token_shape"
POS_COL="pos"
NER_COL="ner"

filename="model/crf_swe.pickle"

file = open(filename, 'rb')
crf = pickle.load(file)
file.close()

print("Loaded " + filename )


r = RDRPOSTagger()

r.constructSCRDRtreeFromRDRfile("./model/Swedish.RDR")

DICT = readDictionary("./model/Swedish.DICT")
sent = ""
while True:
    print()
    sent = input("Give a sentence in Swedish (q to exit): ")
#     sent = "Kalle tycker om Sverige."
    if sent in ['q']:
        break
    tokenized_sent = nltk.word_tokenize(sent)


    split_sent = ""
    for token in tokenized_sent:
        split_sent = split_sent + " " + token

    posTagged = r.tagRawSentence(DICT, split_sent)
    posTaggedSplit=posTagged.split()
    tokens=[]
    posTags=[]
    # print(posTaggedSplit)
    for posTaggedToken in posTaggedSplit:
        splitToken = posTaggedToken.split("/")
        token = splitToken[0]
        tokens.append(token)
        pos = splitToken[1].split('.')[0]
        posTags.append(pos)
    # print(tokens)
    # print(posTags)
#     print(tokens)
#     print(posTags)
    
    data=[]
    for i in range(len(tokens)):
        word = tokens[i]
        pos = posTags[i]
        ner = "unknown"
        data.append([1,word,pos,ner])
#     print(data)

    df = pd.DataFrame(data, columns = [ SENT_COL, TOKEN_COL, POS_COL, NER_COL ]) 


    analyseTokens(df)

    getter_sent = SentenceGetter(df)
    pred_sentence = getter_sent.sentences

    X_sent = [sent2features(s) for s in pred_sentence]
    # y = [sent2labels(s) for s in sentences]
#     print(X_sent)
    y_pred = crf.predict(X_sent)[0]
#     print(y_pred)
    # print("done")
    df[NER_COL]=y_pred
    df = df.drop([SENT_COL,SHAPE_COL], axis=1)

    df.rename(columns={TOKEN_COL:TOKEN_COL.upper(),POS_COL:POS_COL.upper(),NER_COL:NER_COL.upper()}, 
                     inplace=True)
    print("\n")
    print(df)
print("\nWhat would it mean if you got to quit?")