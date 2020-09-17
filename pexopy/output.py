from numpy import genfromtxt, array
import os



class EmulationOutput(object):
   """
   Read PEXO emulation output file from the specified `path`.
   """
   def __init__(self, path):
      if not os.path.isfile(path):
         errormessage = "PEXO output not found in the specified path: {}".format(path)
         raise FileNotFoundError(errormessage)
      
      self.path = path
      self.data = self._read(path)


   def saveto(self, path):
      from shutil import copyfile
      copyfile(self.path, path)


   def _read(self, path):
      return genfromtxt(path, names=True)



class FitOutput(object):
   """
   Read PEXO fit output file from the specified `path`.
   """
   def __init__(self, path):
      if not os.path.isfile(path):
         errormessage = "PEXO output not found in the specified path: {}".format(path)
         raise FileNotFoundError(errormessage)

      self.path = path
      self.data = self._read(path)


   def _read(self, path):
      self.data = genfromtxt(path, names=True)
