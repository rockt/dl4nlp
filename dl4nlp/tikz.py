from dl4nlp.display import Image
import os
import random
import numpy as np
import torch
from torch.autograd import Variable

tikzstandalone = r"""
\documentclass[tikz]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

\input{packages}
\input{macros_full}

\begin{document}
\begin{tikzpicture}[x=1cm,y=1cm, node distance=2cm and 2cm, -Latex, very thick, auto]
    %s
\end{tikzpicture}
\end{document}

"""


def tikz(body, filename=str(random.randint(0, 1e8)), directory="/tmp/tikzmagic/", dpi=600, width=None, height=None,
         display_width=None, display_height=None):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory + "%s.tex" % filename, "w") as f:
        f.write(tikzstandalone % body)
    widthstr = str(width) if width is not None else ""
    heightstr = str(height) if height is not None else ""
    rescale = " -resize %sx%s" % (widthstr, heightstr) if width is not None or height is not None else ""

    os.system("cp tex/*.tex %s;" % directory +
              "cd %s; " % directory +
              "pdflatex -interaction=nonstopmode %s.tex; " % filename +
              "convert%s -density %d %s.pdf %s.png" % (rescale, dpi, filename, filename))

    return Image("%s%s.png" % (directory, filename), width=display_width, height=display_height)


def get_color(p, xmin=-1, xmax=1, upper_color="nice-blue", lower_color="nice-red", center_color="nice-yellow"):
    diff = xmax - xmin
    color = ""
    p = (p - xmin) / diff * 100
    if p < 50:
        color = "%s!%2.2f!%s" % (lower_color, (100 - p - 50) * 2, center_color)
    else:
        color = "%s!%2.2f!%s" % (upper_color, (p - 50) * 2, center_color)
    return color


def plot_matrix(M, xmin=None, xmax=None):
    if isinstance(M, Variable):
        M = M.data
    if xmin is None or xmax is None:
        xmin = M.min()
        xmax = M.max()
    diff = xmax - xmin
    tmp = ""
    for i in range(M.size(0)):
        ix = M.size(0) - i - 1
        for j in range(M.size(1)):
            color = get_color(M[ix, j], xmin, xmax)
            value = "%d" % M[ix, j] if isinstance(M, torch.LongTensor) else "%2.2f" % M[ix, j]
            tmp += "\draw[fill=%s] (-0.5+%d, %d) rectangle (0.5+%d, %d);\n" % (color, j, i, j, i + 1)
            tmp += r"\node[] at (%d, %d+0.5) {%s};" % (j, i, value) + "\n"
    return tmp


def plot_vec(v, xmin=None, xmax=None):
    if xmin is None or xmax is None:
        xmin = v.min()
        xmax = v.max()
    diff = xmax - xmin
    tmp = ""
    for i in range(len(v)):
        color = get_color(v[i], xmin, xmax)
        tmp += "\draw[fill=%s] (-0.5, %d) rectangle (0.5, %d);\n" % (color, i, i + 1)
        tmp += r"\node[] at (0.0, %d+0.5) {%2.2f};" % (i, v[i]) + "\n"
    return tmp


def ticks(xticks=None, yticks=None):
    tmp = ""
    if xticks is not None:
        for i, x in enumerate(xticks):
            tmp += r"\node[anchor=north] at (%d, 0) {%s};" % (i, x)
    if yticks is not None:
        for i, y in enumerate(yticks):
            ix = len(yticks) - i
            tmp += r"\node[anchor=east] at (-0.5, %d-0.5) {%s};" % (ix, y)
    return tmp


def labels(M, xlabel=None, ylabel=None):
    ysize, xsize = M.size()
    tmp = ""
    if xlabel is not None:
        tmp += r"\node[anchor=north] at (%f-0.5,0) {%s};" % (xsize / 2.0, xlabel)
    if ylabel is not None:
        tmp += r"\node[anchor=east] at (-0.5,%f) {%s};" % (ysize / 2.0, ylabel)
    return tmp


def plot_tikz(xs, xdist=1, ydist=1):
    tmp = ""
    yshift = 0
    for l, M in enumerate(xs):
        assert len(M.size()) == 2
        # todo: get max and min value in matrix and color vector accordingly
        xmax = M.max()
        xmin = M.min()
        if yshift > 0:
            tmp += r"\begin{scope}[shift={(0,%d)}]" % yshift + "\n"
        for i in range(M.size(0)):
            tmp += r"\begin{scope}[shift={(%d,0)}]" % (i * (xdist + 1)) + "\n"
            tmp += plot_vec(M[i, :], xmin, xmax)
            tmp += r"\end{scope}" + "\n"
        if yshift > 0:
            tmp += r"\end{scope}" + "\n"
        yshift += M.size(1) + ydist
    return tmp


def shift(tikz, x=0, y=0):
    return r"\begin{scope}[shift={(%d,%d)}]" % (x, y) + "\n" + tikz + r"\end{scope}" + "\n"
