SENT_COL="sent"
TOKEN_COL="token"
SHAPE_COL="token_shape"
POS_COL="pos"
NER_COL="ner"

class SentenceGetter(object):
    
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, p, t,s) for w, p, t,s in zip(s[TOKEN_COL].values.tolist(),
                                                           s[POS_COL].values.tolist(),
                                                           s[NER_COL].values.tolist(),
                                                           s[SHAPE_COL].values.tolist())]
        self.grouped = self.data.groupby(SENT_COL).apply(agg_func)
        self.sentences = [s for s in self.grouped]
    
    def get_next(self):
        try:
            s = self.grouped[self.n_sent]
            self.n_sent += 1
            return s
        except:
            return None

def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    shapetag = sent[i][3]
    

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'shapetag': shapetag,
        'shapetag[:2]': shapetag,
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        shapetag1 = sent[i-1][3]
        
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:shapetag': shapetag1,
            '-1:shapetag[:2]': shapetag1[:2],
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        shapetag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
             '+1:shapetag': shapetag1,
            '+1:shapetag[:2]': shapetag1[:2],
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label, shape in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]

def analyseTokens(df):
    #tokens = ["\"","'",",",".","-","_"]
    new_token_col = []
    for token in df[TOKEN_COL]:
        #print(token)
        token=token.strip()
        token_shape = ""
        if len(token) == 1 and not token.isalnum():
            token_shape = "sign" # or =token
        else:
            if token.isupper():
                token_shape="X"
            elif token[0].isupper():
                token_shape="Xx"
            else:
                token_shape="x"
            if token[len(token)-1] == ".":
                token_shape+="."
        new_token_col.append(token_shape)
    #print(len(new_token_col))
    df[SHAPE_COL]=new_token_col