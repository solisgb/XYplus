# -*- coding: Latin-1 -*-
"""
Created on Tue May  1 10:54:23 2018

Se hacen gráficos temporales con la librería matplotlib

Tipos
1) XY distingiendo medidas la situación de las medidas piezométricas
2) XY en que se asocia al código principal otras series relacionadas en el
   mismo subplot

@author: solis
"""

import log_file as lf


def select_project(FILENAME):
    """
    lee el fichero xml FILENAME, muestra los proyectos para que el usuario
        escoja uno de ellos

    input
    FILENAME: fichero xml de estructura adecuada situada donde se encuentran
        los scripts del programa

    return:
        el proyecto seleccionado por el usuario con un árbol xml
    """
    import xml.etree.ElementTree as ET
    tree = ET.parse(FILENAME)
    root = tree.getroot()

    print('Projects in ' + FILENAME)
    projects = []
    for i, project in enumerate(root.findall('project')):
        projects.append(project)
        print(i, end=' ')
        print('. ' + project.get('name'))
    print('Select project number:', end=' ')
    choice = input()
    return projects[int(choice)]


def make_graphs(project):
    """
    selecciona los patos para los gráficos y llama a lafunción que dibuja
    los gráficos con el modulo matplotlib

    input
        project: es el tag del fichero XYplus_parameters.f_xml seleccionado
            en XYplus_main
    """
    from os.path import join
    import pyodbc
    import db_con_str
    from time_series import XYt_1
    import XYplus_parameters as par

    db = project.find('db').text
    con = pyodbc.connect(db_con_str.con_str(db))

    cur = con.cursor()
    select_master = project.find('select_master').text.strip()
    cur.execute(select_master)

    id_col = int(project.find('select_master').get('id_column')) - 1

    cur2 = con.cursor()
    ifecha = int(project.find('select_data').get('fecha_column')) - 1
    ivalue = int(project.find('select_data').get('value_column')) - 1
    ylabel = project.find('graph').get('y_axis_name')

    # si la serie distingue entre situacion durante medida
    tags_situacion = project.findall('select_data/situacion')
    situaciones = [tag.text.strip() for tag in tags_situacion]
    if situaciones:
        isitu = int(project.find('select_data/situacion_column').text) - 1
    else:
        isitu = None

    for row in cur:

        # datos de la serie principal
        print(row[id_col])
        ts_4xy = _serie_get(project, row, cur2, row[id_col], ifecha,
                                ivalue, situaciones, isitu)
        if len(ts_4xy) == 0:
            continue

        # datos de otros puntos relacionados con cada punto de la serie
        # principal. Las series se extraen utilizando la misma select
        if par.show_aux == 1:
            tss_aux = _datos_aux_get(project, cur2, row[id_col], ifecha,
                                     ivalue)
            ts_4xy = ts_4xy + tss_aux

        # datos de los umbrales. Son series especiales
        if par.show_hl == 1:
            tss_u = _umbrales_get(project, row[id_col], cur2,
                                  ts_4xy[0].fechas[0],
                                  ts_4xy[0].fechas[-1])
            ts_4xy = ts_4xy + tss_u

        # elementos adicionales del gráfico
        stitle = _title_get(project, row)
        file_name = _file_name_get(project, row)
        dst = join(par.dir_out, file_name)

        # dibuja el gráfico
        XYt_1(ts_4xy, stitle, ylabel, dst)

    con.close()


def _datos_aux_get(project, cur, id1, ifecha, ivalue):
    """
    extrae los datos de otros puntos relacionados con el principal
        los datos de los puntos auxiliares son del mismo tipo que
        la serie principal, ya que se utiliza la misma select

    input
        project: es el tag del fichero XYplus_parameters.f_xml seleccionado
            en XYplus_main
        cur: cursor a la BDD para seleccionar los datos
        id1: código del punto principal, del cual queremos ver si tiene
            otros puntos relacionados
        ifecha: índice de la columna fecha al hacer la select_data
        ivalue: indice de la columna valor (dato a representar en el eje de
            ordenadas) al hacer la select data

    return
    Una lista de objetos Time_series o una lista vacía
    """
    from copy import deepcopy
    from time_series import Time_series
    select_data = project.find('select_data').text.strip()
    select_aux = project.find('select_master_related').text.strip()
    cur.execute(select_aux, id1)
    cods = [row for row in cur]
    tss = []
    for cods1 in cods:
        cur.execute(select_data, cods1[1])
        for row_data in cur:
            xy = [(row_data[ifecha], row_data[ivalue]) for row_data in cur]
            if len(xy) == 0:
                lf.write('{0} no tiene datos'.format(id1))
                continue
            fechas = [xy1[0] for xy1 in xy]
            values = [xy1[1] for xy1 in xy]
            legend = '{}'.format(cods1[1])
            try:
                tmp = Time_series(fechas, values, legend, marker='')
                tss.append(deepcopy(tmp))
            except Exception as error:
                lf.write('{0} error al instanciar el objeto Time_series \
                         con código auxiliar {}'.format(id1, cods1[1]))
                continue
    if not tss:
        lf.write('{0} no tiene series auxiliares'.format(id1))
    return tss


def _serie_get(project, row, cur, id1, ifecha, ivalue, situaciones, isitu):
    """
    hace select a una BDD e instancia un objeto Temporal_series

    input
    project: tag del proyecto seleccionado
    row: fila de select_master correspondiente al punto cuyos umbrales
        queremos representar
    cur: cursor a la BDD para seleccionar los datos
    id1: código del punto cuyos datos cuyos queremos representar
    ifecha: posición de las fechas en el select
    ivalue: posición de los valores en el select
    isituacion: posición de las situaciones en el select puede ser None-
    situaciones: [] valores a considerar en el campo situacion -puede ser
        vacía-

    return
    lista de objetos Time_series; puede ser vacía
    """
    from time_series import Time_series
    select_data = project.find('select_data').text.strip()
    npar = select_data.count('?')
    if npar != 1:
        raise ValueError('select_data debe tener un signo ?')
    cur.execute(select_data, id1)
    if isitu is None:
        xy = [(row_data[ifecha], row_data[ivalue]) for row_data in cur]
    else:
        xy = [(row_data[ifecha], row_data[ivalue],
               row_data[isitu]) for row_data in cur]

    if len(xy) == 0:
        lf.write('{0} tiene datos'.format(id1))
        return []
    else:
        if xy[0][1] is None:
            # si un punto no tiene valor de z y sí de pnp, la operación
            # z-pnp devuelve None
            lf.write('{0} tiene al menos 1 valor nulo, si es un valor \
                     calculado es posible que un término sea nulo'.format(id1))
            return None
    fechas = [xy1[0] for xy1 in xy]
    values = [xy1[1] for xy1 in xy]
    legend = _legend_main_get(project, row)
    if isitu is not None:
        situs = [xy1[2] for xy1 in xy]
        smarker = ' '
    else:
        smarker = '.'
    tss = [Time_series(fechas, values, legend, marker=smarker)]
    for situacion in situaciones:
        fechas2 = [fecha1 for (fecha1, situ1) in zip(fechas, situs)
                   if situ1 == situacion]
        if len(fechas2) == 0:
            lf.write('{} no tiene datos {}'.format(id1, situacion))
            continue
        values2 = [value1 for (value1, situ1) in zip(values, situs)
                   if situ1 == situacion]
        legend = '..{}'.format(situacion)
        tss.append(Time_series(fechas2, values2, legend,
                               marker='.', scatter=1))

    return tss


def _time_series_situaciones_get(tmp, isitu):
    """

    input
    project: tag del proyecto seleccionado
    row: fila de select_master correspondiente al punto cuyos umbrales
        queremos representar
    cur: cursor a la BDD para seleccionar los datos
    id1: código del punto cuyos datos cuyos queremos representar

    return
    [] de objetos Time_series diferenciados por la situación durante la medida
        , la lista puede ser vacía
    """
    return None


def _umbrales_get(project, id1, cur2, fecha1, fecha2):
    """
    selecciona los datos del umbral o umbrales y crea los correspondientes
        obhetos Time_series

    input:
        project: tag del proyecto seleccionado
        id1: código del punto cuyos umbrales cuyos queremos representar
        row: fila de select_master correspondiente al punto cuyos umbrales
            queremos representar
        cur2: cursor a la BDD para seleccionar los datos

    return:
        una lista de objetos Time_series, o una lista vacía
    """
    from copy import deepcopy
    from time_series import Time_series
    select_umbrales = project.find('select_umbrales').text.strip()
    umbral_col = int(project.find('select_umbrales').get('umbral_column')) - 1
    if select_umbrales.count('?') != 3:
        raise ValueError('select_umbrales debe tener 3 signos ?')
    line_styles = (':', '-.', '--')
    ts = []
    j_ls = -1
    for i, umbral in enumerate(project.findall('select_umbrales/umbral')):
        parametro = umbral.get('parametro').strip()
        cod_u = umbral.get('cod').strip()
        cur2.execute(select_umbrales, (id1, cod_u, parametro))
        row1_u = cur2.fetchone()
        if row1_u is None:
            lf.write('{} no tiene umbral: {}, {}'.format(id1, cod_u,
                     parametro))
            continue
        # todos los umbrales se ponen en el rango de fechas de cada sondeo
        # si se desea ponerlo en su rango específico debe escribirse una
        # función ad hoc extrayendo los datos de la tabla umbrales
        fechas = [fecha1, fecha2]
        values = [row1_u[umbral_col], row1_u[umbral_col]]
        legend = _legends_umbrales_get(project, row1_u, i)
        j_ls += 1
        try:
            tmp = Time_series(fechas, values, legend, marker='',
                              slinestyle=line_styles[j_ls])
            ts.append(deepcopy(tmp))
            if j_ls == 2:
                j_ls = -1
        except Exception as error:
            lf.write('{0} error al instanciar el objeto Time_series \
                     para {}'.format(id1, legend))
            continue
    if not ts:
        lf.write('{0} no tiene umbrales'.format(id1))
    return ts


def _title_get(project, row):
    """
    forma el título de un gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es fila activa devuelta por select_master) de donde se
            extrae el título del gráfico

    return
        un str con el título del gráfico (puede tener más de una línea)
    """
    titles = project.findall('graph/title')
    if len(titles) == 0:
        return ""
    stitles = [title.text.strip() for title in titles]
    for i, title in enumerate(titles):
        cols = title.findall('column')
        if len(cols) == 0:
            stitles[i] = title.text.strip()
            continue
        subs = [row[int(col.text)-1] for col in cols]
        stitles[i] = stitles[i].format(*subs)
    return '\n'.join(stitles)


def _legend_main_get(project, row):
    """
    forma la leyenda de la serie principal del gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es fila activa devuelta por select_master) de donde se
            extrae el título del gráfico

    return
        un str con la leyenda del punto principal del gráfico
    """
    legend_master = project.find('graph/legend_master').text.strip()
    columns_master = project.findall('graph/legend_master/column')
    if len(columns_master) == 0:
        return legend_master
    subs = [row[int(col1.text)-1] for col1 in columns_master]
    return legend_master.format(*subs)


def _legends_umbrales_get(project, row1_u, ilegend):
    """
    forma la leyenda de uno de los umbrales

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row1_u: es la fila devuelta para un punto después de ejecutar la
            select select_umbrales del fichero XYplus_parameters.f_xml
        ilegend: es un int que define el número de umbral para el punto

    return
        un str con la leyenda
    """
    legend_tag = project.find('graph/legend_umbrales')
    legend_mold = legend_tag.text.strip()
    len_legend_mold = len(legend_mold)
    col_tags = legend_tag.findall('column')
    n_cols = len(col_tags)
    if len_legend_mold == 0:
        return 'Leg. {0:d}'.format(ilegend)
    else:
        if n_cols == 0:
            return legend_mold
        else:
            subs = [row1_u[int(col.text)-1] for col in col_tags]
            return legend_mold.format(*subs)


def _file_name_get(project, row):
    """
    forma el nombre de cada fichero de gráfico

    input
        project: es el tag project del proyecto seleccionado
            en fichero XYplus_parameters.f_xml -en XYplus_main.py-
        row: es la fila de un punto que devuelve la select
            select_master del fichero XYplus_parameters.f_xml

    return
        sname: str que contiene el nombre del fichero
    """
    fname = project.find('select_master/file_name').text.strip()
    tcols = project.findall('select_master/file_name/column')
    subs = [row[int(tcol.text)-1] for tcol in tcols]
    sname = fname.format(*subs)
    return sname


def validate_parameters():
    """
    comprueba la validez de las variables definidas en el módulo
        XYplus_parameters
    """
    import XYplus_parameters as par
    from os.path import isdir, exists

    PREFIJO_F_XML = 'XYplus'

    def validate_date(sdate: str, variable_name: str):
        """
        a partir de un str con formato "dd/mm/yyyy" devuelve un objeto date
        """
        from datetime import date
        if sdate == 'now':
            sdate = date.today().strftime('%d/%m/%Y')
        ws = sdate.split('/')
        try:
            return date(int(ws[2]), int(ws[1]), int(ws[0]))
        except Exception as error:
            raise ValueError('La variable {} está mal escrita'.
                             format(variable_name))

    if not exists(par.f_xml):
        raise ValueError('No existe {}'.format(par.f_xml))
    else:
        if par.f_xml[0:6] != PREFIJO_F_XML:
            raise ValueError('{} debe empezar por {}'.format(par.f_xml,
                             PREFIJO_F_XML))
    if not isdir(par.dir_out):
        raise ValueError('No existe {}'.format(par.dir_out))
    if par.show_hl not in (0, 1):
        raise ValueError('La variable show_hl debe ser 0 o 1')
    if par.show_aux not in (0, 1):
        raise ValueError('La variable show_aux debe ser 0 o 1')
    par.date_1 = validate_date(par.date_1, 'date_1')
    par.date_2 = validate_date(par.date_2, 'date_2')
    if par.date_1 >= par.date_2:
        raise ValueError('date_1 debe ser < que date_2')
