from numpy import genfromtxt
from .settings import out_storage
import os


class PexoOut(object):
   """
   Read PEXO output file from the specified `path`.
   """
   def __init__(self):
      self._storage = out_storage


   def read(self, path):
      if not os.path.isfile(path):
         # errormessage = f"PEXO output not found in the specified path: {path}" # python 3+
         errormessage = "PEXO output not found in the specified path: {}".format(path) # python 2.7
         raise FileNotFoundError(errormessage)

      return genfromtxt(path, names=True)