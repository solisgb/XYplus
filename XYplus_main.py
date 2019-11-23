# -*- coding: utf-8 -*-
"""
Driver XYplus.py; script para hacer graficos temporales

@solis
"""
import log_file as lf

if __name__ == "__main__":

    try:
        from datetime import timedelta
        from time import time
        from XYplus import select_project, make_graphs, validate_parameters
        from XYplus_parameters import f_xml

        validate_parameters()
        project = select_project(f_xml)
#        if project is None:
#            raise ValueError('El usuario no ha seleccionado un proyecto válido')

        startTime = time()

        make_graphs(project)

        xtime = time()-startTime
        print('The script took {0}'.format(str(timedelta(seconds=xtime))))
    except Exception as e:
        import traceback
        print(e)
        MSG = '\n{}'.format(traceback.format_exc())
        lf.write(MSG)
    finally:
        lf.to_file()
        print('fin; se ha generado el fichero log.txt')
