import IPython.display
import os

tikzstandalone = r"""
\documentclass[tikz]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

\input{/Users/rockt/workspace/rockt-thesis/thesis/packages}
\input{/Users/rockt/workspace/rockt-thesis/thesis/macros}

\begin{document}
\begin{tikzpicture}[x=1cm,y=1cm, node distance=2cm and 2cm, -Latex, very thick, auto]
  \draw[line width = 3pt, dashed, opacity=0.5] (-1,1) rectangle (3.5,9);
  \node[opacity=0.5, anchor=north east] at (3.5,9) {\Large RNN cell};
  \node[input] (x) {$\vec{x}_t$};
  \node[cnode, above of = x] (cons) {$\vec{z}_t$};
  \node[input, left of = cons] (s) {$\vec{s}_{t-1}$};
  \draw[] (x) -- (cons) node[op right] {$\cons$};
  \draw[] (s) -- (cons);

  \node[cnode, above of = cons] (mul) {$u_1$};
  \node[param, right of = mul] (W) {$\mat{W}$};
  \draw[] (cons) -- (mul) node[op right] {$\mul$};
  \draw[] (W) -- (mul);

  \node[cnode, above of = mul] (add) {$u_2$};
  \node[param, right of = add] (b) {$\vec{b}$};
  \draw[] (mul) -- (add) node[op right] {$+$};
  \draw[] (b) -- (add);

  \node[cnode, above of = add] (tanh) {$u_3$};
  \draw[] (add) -- (tanh) node[op right] {$\ntanh$};

  \node[output, above of = tanh] (h) {$\vec{h}_t$};
  \node[output, right = 3.5cm of cons] (st) {$\vec{s}_t$};

  \draw[] (tanh) -- (h);
  \draw[] (tanh) -| ($(cons)!0.65!(st)$) -- (st);
\end{tikzpicture}
\end{document}

"""

with open("figures/generated/test.tex", "w") as f:
    f.write(tikzstandalone)

os.system("cd figures/generated; latexmk test.tex")

IPython.display.Image("figures/proprietary/sequences.jpg")