from numpy import genfromtxt, array
from rpy2.robjects import r
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
        self.data = genfromtxt(path, names=True)


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
        self.data = r.load(path)


    def saveto(self, path):
        move(self.path, path)
        self.path = path


    @property
    def parstat(self):
        parstat  = array(r['ParStat']).T
        colnames = r.colnames(parstat)
        properties = ["xopt", "x1per", "x99per", "x10per", "x90per", "xminus", "xplus", "mode", "mean", "sd", "skewness", "kurtosis"]
        
        parameter_values = [dict(zip(properties, parstat[i])) for i in range(len(colnames))]
        return Struct(dict(zip(colnames, parameter_values)))


    @property
    def mc(self):
        raise NotImplementedError


    @property
    def data(self):
        raise NotImplementedError


    @property
    def model(self):
        raise NotImplementedError
