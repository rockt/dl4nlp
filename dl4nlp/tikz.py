from dl4nlp.display import Image
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
