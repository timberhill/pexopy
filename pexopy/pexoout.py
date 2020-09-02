from numpy import genfromtxt, array
from .settings import temp_storage
import os


class PexoOutput(object):
   """
   Read PEXO output file from the specified `path`.
   """
   def __init__(self, path, utc):
      self._storage = temp_storage
      self._read(path)
      self.utc = utc


   def _read(self, path):
      if not os.path.isfile(path):
         # errormessage = f"PEXO output not found in the specified path: {path}" # python 3+
         errormessage = "PEXO output not found in the specified path: {}".format(path) # python 2.7
         raise FileNotFoundError(errormessage)

      self.data = genfromtxt(path, names=True)
   

   def plot_timing(self, saveto=None, show=False, **kwargs):
      import matplotlib.pyplot as plt
      secondsPerDay = 24 * 3600
      
      if len(array(self.utc).shape) == 1:
         utc1 = array([int(x) for x in self.utc.T])
         utc2 = array([x-int(x) for x in self.utc.T])
      elif len(array(self.utc)) == 2:
         utc1 = self.utc[0]
         utc2 = self.utc[1]
      
      diff1 = (self.data["BJDtdb1"] - utc1) * secondsPerDay
      diff2 = self.data["BJDtdb2"]*secondsPerDay - utc2*secondsPerDay
      
      f, ax = plt.subplots(1, 1)
      ax.plot(utc1+utc2, diff1+diff2, "k-", **kwargs)
      ax.set_xlabel("JD[UTC], days")
      ax.set_ylabel("JD[TDB]-JD[UTC], sec")

      if saveto is not None:
         plt.savefig(saveto)

      if show:
         plt.show()

      return f, ax
