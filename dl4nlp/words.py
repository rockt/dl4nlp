import numpy as np
import pandas as pd


def get_counts(contexts):
    vocab = {}
    id2word = []
    f = {}
    context_size = 3
    for context in contexts:
        for word in context:
            if word not in vocab:
                vocab[word] = len(vocab)
                id2word.append(word)
    for word in vocab:
        f[word] = np.zeros(len(vocab))
    for context in contexts:
        for i, word in enumerate(context):
            for j in range(max(i-context_size, 0), min(i+context_size, len(context))):
                if i != j:
                    f[word][vocab[context[j]]] += 1
    return f, vocab, id2word


def to_df(f, id2word):
    d = {}
    for word in id2word:
        d[word] = pd.Series(f[word], index=id2word)
    return pd.DataFrame(d).transpose()
