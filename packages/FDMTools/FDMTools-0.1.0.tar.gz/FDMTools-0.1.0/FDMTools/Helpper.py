import math
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def GenFigure(PlotPars):
    nRows = math.ceil(np.sqrt(len(PlotPars)))
    nCols = math.ceil(len(PlotPars) / nRows)
    fig, Axs = plt.subplots(nrows=nRows, ncols=nCols, figsize=(12, 8))
    if nRows == 1 and nCols == 1:
        Axs = [Axs, ]
    else:
        Axs = Axs.flatten()

    return fig, Axs


def PlotYield(dfDat, BoxPlotFunct=sns.stripplot, HueVar='IdsChar', PlotPars=None):
    if PlotPars is None:
        dc = list(dfDat.columns)
        for i in ('ChName', 'Col', 'Row', 'ChIndex'):
            dc.remove(i)
        PlotPars = dc

    fig, Axs = GenFigure(PlotPars)
    for ic, par in enumerate(PlotPars):
        BoxPlotFunct(data=dfDat,
                     x='Col',
                     y=par,
                     hue=HueVar,
                     ax=Axs[ic])

    fig.tight_layout()
    fig, Axs = GenFigure(PlotPars)
    for ic, par in enumerate(PlotPars):
        Axs[ic].set_title(par)
        sns.heatmap(data=dfDat.pivot(index='Row', columns='Col', values=par),
                    # annot=True,
                    ax=Axs[ic])
    fig.tight_layout()
