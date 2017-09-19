import IPython.display
import os
import random

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


def tikz(body, filename=str(random.randint(0, 1e8)), directory="/tmp/tikzmagic/", dpi=600, width=None, height=None):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(directory + "%s.tex" % filename, "w") as f:
        f.write(tikzstandalone % body)

    os.system("cp tex/*.tex %s;" % directory +
              "cd %s; " % directory +
              "pdflatex -interaction=nonstopmode %s.tex; " % filename +
              "convert -density %d %s.pdf %s.png" % (dpi, filename, filename))

    return IPython.display.Image("%s%s.png" % (directory, filename), width=width, height=height)
