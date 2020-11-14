from numpy import genfromtxt, array, asarray
from rpy2.robjects import r
from rpy2.rinterface import NARealType
from shutil import move
import os

from .struct import Struct


class EmulationOutput(object):
    """
    Read PEXO emulation output file (.txt) from the specified `path`.
    """
    def __init__(self, path):
        if not os.path.isfile(path):
            errormessage = "PEXO output not found in the specified path: {}".format(path)
            raise FileNotFoundError(errormessage)
        
        self.path = path
        self.contents = genfromtxt(path, names=True)


    def saveto(self, path):
        move(self.path, path)
        self.path = path



class FitOutput(object):
    """
    Read PEXO fit output file (.Robj) from the specified `path`.
    """
    def __init__(self, path):
        if not os.path.isfile(path):
            errormessage = "PEXO output not found in the specified path: {}".format(path)
            raise FileNotFoundError(errormessage)

        self.path = path
        self.contents = r.load(path)


    def saveto(self, path):
        move(self.path, path)
        self.path = path


    @property
    def parstat(self):
        obj  = array(r['ParStat']).T
        colnames = r.colnames(obj)
        properties = ["xopt", "x1per", "x99per", "x10per", "x90per", "xminus", "xplus", "mode", "mean", "sd", "skewness", "kurtosis"]

        parameter_values = [dict(zip(properties, obj[i])) for i in range(len(colnames))]
        return Struct(dict(zip(colnames, parameter_values)))


    @property
    def mc(self):
        r_obj     = r['mc']
        colnames  = r.colnames(r_obj)
        obj       = array(r_obj).T

        return Struct(dict(zip(colnames, obj)))


    @property
    def data(self):
        def _fix_nones_list(column_list):
            return [None if isinstance(x, NARealType) else x for x in column_list]

        r_obj     = r['Data']
        colnames  = r.colnames(r_obj)
        table = [_fix_nones_list(x) for x in r_obj]

        return Struct(dict(zip(colnames, table)))


    @property
    def model(self):
        def _fix_nones_list(column_list):
            return [None if isinstance(x, NARealType) else x for x in column_list]

        r_obj     = r['model']
        colnames  = r.colnames(r_obj)
        table = [_fix_nones_list(x) for x in r_obj]

        return Struct(dict(zip(colnames, table)))
