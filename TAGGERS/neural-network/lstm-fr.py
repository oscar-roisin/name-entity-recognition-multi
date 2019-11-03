import numpy as np
import pandas as pd

sents = np.loadtxt('./DATA/sent_french.txt', delimiter='\t', dtype=str)

data = pd.DataFrame(sents, columns=['Sentence #', 'Word', 'POS', 'Tag'], copy=True)
data['Sentence #'] = data['Sentence #'].astype('int')
print(data.head())

words = list(set(data["Word"].values))
words.append("ENDPAD")

n_words = len(words)
print(n_words)

tags = list(set(data["Tag"].values))

n_tags = len(tags)
print(n_tags)

class SentenceGetter(object):
    
    def __init__(self, data):
        self.n_sent = 1
        self.data = data
        self.empty = False
        agg_func = lambda s: [(w, p, t) for w, p, t in zip(s["Word"].values.tolist(),
                                                          s["POS"].values.tolist(),
                                                          s["Tag"].values.tolist()
                                                          )]
        self.grouped = self.data.groupby("Sentence #").apply(agg_func)
        self.sentences = [s for s in self.grouped]

getter = SentenceGetter(data)

sentences = getter.sentences
print(sentences[0])
len(sentences)

import matplotlib.pyplot as plt
plt.style.use("ggplot")

plt.hist([len(s) for s in sentences], bins=50)
plt.show()

sentences = list(filter(lambda s: len(s)<=100, sentences))

plt.hist([len(s) for s in sentences], bins=50)
plt.show()

max_len = 100
word2idx = {w: i for i, w in enumerate(words)}
tag2idx = {t: i for i, t in enumerate(tags)}

from keras.preprocessing.sequence import pad_sequences
X = [[word2idx[w[0]] for w in s] for s in sentences]

X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

y = [[tag2idx[w[2]] for w in s] for s in sentences]

y = pad_sequences(maxlen=max_len, sequences=y, padding="post", value=tag2idx["O"])

from keras.utils import to_categorical

y = [to_categorical(i, num_classes=n_tags) for i in y]

from sklearn.model_selection import train_test_split

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1)

from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional

input = Input(shape=(max_len,))
model = Embedding(input_dim=n_words, output_dim=50, input_length=max_len)(input)
model = Dropout(0.1)(model)
model = Bidirectional(LSTM(units=100, return_sequences=True, recurrent_dropout=0.1))(model)
out = TimeDistributed(Dense(n_tags, activation="softmax"))(model)  # softmax output layer

model = Model(input, out)
model.summary()

model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])

history = model.fit(X_tr, np.array(y_tr), batch_size=64, epochs=5, validation_split=0.2, verbose=1)

model.save('lstm-fr.h5')

hist = pd.DataFrame(history.history)

plt.figure(figsize=(12,12))
plt.plot(hist["acc"])
plt.plot(hist["val_acc"])
plt.show()