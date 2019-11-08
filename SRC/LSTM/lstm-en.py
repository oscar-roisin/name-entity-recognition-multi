import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, precision_score, f1_score
import matplotlib.pyplot as plt
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from keras.models import Model, Input, load_model
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Dropout, Bidirectional

sents = np.loadtxt('./DATA/sent_english.txt', delimiter='\t', dtype=str)

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

def join_sentences(data):
	agg_func = lambda s: [(w, p, t) for w, p, t in zip(s["Word"].values.tolist(),
                                                    s["POS"].values.tolist(),
                                                    s["Tag"].values.tolist()
                                                    )]
	grouped = data.groupby("Sentence #").apply(agg_func)
	return [s for s in grouped]

sentences = join_sentences(data)
print(sentences[0])
print(len(sentences))

plt.style.use("ggplot")
plt.hist([len(s) for s in sentences], bins=50)
plt.show()

sentences = list(filter(lambda s: len(s)<=40, sentences))
print(len(sentences))

plt.hist([len(s) for s in sentences], bins=50)
plt.show()

max_len = 40
word2idx = {w: i for i, w in enumerate(words)}
tag2idx = {t: i for i, t in enumerate(tags)}

X = [[word2idx[w[0]] for w in s] for s in sentences]
X = pad_sequences(maxlen=max_len, sequences=X, padding="post", value=n_words - 1)

y = [[tag2idx[w[2]] for w in s] for s in sentences]
y = pad_sequences(maxlen=max_len, sequences=y, padding="post", value=tag2idx["O"])
y = [to_categorical(i, num_classes=n_tags) for i in y]

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.1)

input = Input(shape=(max_len,))
model = Embedding(input_dim=n_words, output_dim=50, input_length=max_len)(input)
model = Dropout(0.1)(model)
model = Bidirectional(LSTM(units=100, return_sequences=True, recurrent_dropout=0.1))(model)
out = TimeDistributed(Dense(n_tags, activation="softmax"))(model)  # softmax output layer
model = Model(input, out)
model.summary()
model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])

history = model.fit(X_tr, np.array(y_tr), batch_size=64, epochs=5, validation_split=0.2, verbose=1)
model.save('./SRC/LSTM/lstm-en.h5')
hist = pd.DataFrame(history.history)

plt.figure(figsize=(12,12))
plt.plot(hist["accuracy"])
plt.plot(hist["val_accuracy"])
plt.savefig('./SRC/LSTM/accuracy-en.png')
plt.show()

model = load_model('./SRC/LSTM/lstm-en.h5')

pred = model.predict(X)

y_num = [np.argmax(s, axis=1) for s in y]
y_num = np.array(y_num).flatten()
pred_num = [np.argmax(s, axis=1) for s in pred]
pred_num = np.array(pred_num).flatten()

filterNotNE = np.argwhere(y_num!=tag2idx['O'])
filterNotNE = filterNotNE.reshape(filterNotNE.shape[0])

print('Precision =', precision_score(y_num[filterNotNE], pred_num[filterNotNE], average='weighted'))
print('Recall =', recall_score(y_num[filterNotNE], pred_num[filterNotNE], average='weighted'))
print('F1-Score =', f1_score(y_num[filterNotNE], pred_num[filterNotNE], average='weighted'))