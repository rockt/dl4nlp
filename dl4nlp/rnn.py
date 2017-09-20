import torch
from torch import nn
import torch.nn.functional as F


batch_size, seq_length, k_in, k_out, vocab_size = (3, 5, 2, 3, 9)
emb = nn.Embedding(vocab_size, k_in)


def rnn(cell, X, s0):
    st = s0
    H = []
    S = []
    for i in range(X.size(1)):
        ht, st = cell(X[:,i,:], st)
        H.append(ht)
        S.append(st)
    return H, S

Wu = nn.Linear(k_in+k_out, k_out)
Wr = nn.Linear(k_in+k_out, k_out)
Wx = nn.Linear(k_in, k_out)
Wh = nn.Linear(k_out, k_out)


def gru_cell(xt, st1):
    ht1 = st1
    zt = torch.cat([xt, ht1], dim=1)
    ut = F.sigmoid(Wu(zt))
    rt = F.sigmoid(Wr(zt))
    nt = F.tanh(Wx(xt)) + rt * (Wh(ht1))
    ht = ut * ht1 + (1-ut) * nt
    st = ht
    return ht, st