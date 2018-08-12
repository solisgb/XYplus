# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 09:22:00 2018
@author: Luis Solis

Serie temporal para gráficos con el módulo matplotlib
"""


class Time_series():
    """
    define los datos y sus atributos para ser representados en un
        gráfico
    """
    def __init__(self, fechas: [], values: [], legend: str,
                 marker: str = 'd', line: str = '-'):
        """
        fechas: lista de dates
        values: lista de floats o integeres
        legend: leyenda de la serie
        marker: marcador de la serie en el gráfico
        line: marcador de la línea de un gráfico
        """
        from copy import deepcopy
        import matplotlib
        if len(fechas) != len(values):
            raise ValueError('fechas y values != longitud')
#        colors_array = list(matplotlib.colors.cnames.keys())
        if marker not in matplotlib.markers.MarkerStyle.markers:
            marker = 'd'
        if line not in matplotlib.lines.lineStyles:
            line = '-'
        self.fechas = deepcopy(fechas)
        self.values = deepcopy(values)
        self.legend = legend
        self.line = line
        self.marker = marker


def XYt_1(t_series: [], stitle: str, ylabel: str, dst: str):
    """
    dibuja un gráfico xy de una o más series

    input
        t_series: lista de objetos Time_series; el primer elemento se
            considera la series principal
        stitle: título del gráfico
        ylabel: título del eje Y
        dst: directorio donde se graba el gráfico (debe existir)
    """
    import matplotlib.pyplot as mpl
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dateFmt = mdates.DateFormatter('%d-%m-%Y')

    fig, ax = plt.subplots()
    # El primer objeto es el principal
    for ts1 in t_series:
        ax.plot(ts1.fechas, ts1.values, marker=ts1.marker, label=ts1.legend)

    plt.ylabel(ylabel)
    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.xaxis.set_major_formatter(dateFmt)
    ax.set_title(stitle)
    mpl.legend(loc='best', framealpha=0.5)
    mpl.tight_layout()
    mpl.grid(True)

    fig.savefig(dst)
    plt.close('all')
