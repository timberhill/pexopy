from .uniquefilename import UniqueFile
from .settings import temp_storage
import numbers
import os


class ParFile(object):
   """
   PEXOpy .par file handler.
   The constructor's `par` argument is either a dictionary with the parameters, or a path to a file with the parameters.

   If it's a path, the file is parsed and validated.

   If it's a dictionary, it's validated and saved to a file.
   You can also just add parameters as function arguments.

   Either way, the class instance has both the path (<ParFile.path>) and the dictionary (<ParFile.contents>).
   """
   def __init__(self, par={}, **args):
      self._storage = temp_storage
      self.temporary = False
      
      if isinstance(par, type(self)):
         self.contents = par.contents
         self.path = par.path
      elif isinstance(par, str): # this is a path to a file
         self.contents = self._parse_par(par)
         self.path = par
      elif isinstance(par, dict): # this is a dictionary with the parameters
         par.update(args)
         self.contents = par
         self.path = self._generate_par(par)
      else:
         raise ValueError("`par` argument is either a dictionary with the parameters, or a path to a file with the parameters.")


   def _validate_parameter(self, name, value, error=""):
      if name not in self._par: # unknown parameter
         errormessage = "{}Unknown parameter '{}'.".format(error, name)
         raise KeyError(errormessage)

      options = self._par[name]["options"]
      param_type = self._par[name]["type"]

      # cover the type-str conversion
      if param_type == bool and isinstance(value, str) and value.lower() == "true":
         value = True
      if param_type == bool and isinstance(value, str) and value.lower() == "false":
         value = False
      if param_type == numbers.Number: # try parsing the string into float 
         value = float(value)

      if options is not None and value not in options: # there are some set options for this parameter
         errormessage = "{}The value of '{}' should be one of {}".format(error, name, options)
         raise ValueError(errormessage)
      
      if not isinstance(value, param_type):
         errormessage = "{}The value of '{}' should be of type {}".format(error, name, param_type)
         raise ValueError(errormessage)


   def _generate_par(self, par_dict):
      self.temporary = True
      contents = ""
      for key in par_dict:
         value = par_dict[key]
         self._validate_parameter(key, value)

         # handle the bool-to-str
         value = str(value).upper() if isinstance(value, bool) else value
         contents += "{} {}\n".format(key, value)

      filename = UniqueFile(contents, append=".par")
      par_path = os.path.join(self._storage, filename)
      
      with open(par_path, "w") as f:
         f.write(contents)

      return par_path


   def _parse_par(self, par_path):
      if not os.path.isfile(par_path):
         errormessage = "File '{}' does not exist.".format(par_path)
         raise IOError(errormessage)

      # read the .par file into a dictionary
      par = {}
      with open(par_path) as f:
         for line in f:
               s = line.split()
               if len(s) != 2:
                  errormessage = "Error while parsing the .par file: {par_path}. Must only have two columns, i.e. 'name value', {} columns encountered.".format(par_path, len(s))
                  raise ValueError()

               self._validate_parameter(s[0], s[1], error="Error while parsing the .par file: {}. ".format(par_path))
               
               # didn't raise an error, all must be good with this parameter
               par[s[0]] = s[1]
         
      return par
   

   def info(self):
      """
      Print information about the parameters
      """
      for key in self._par:
         t = str(self._par["type"])
         o = "" if self._par["options"] is None else ", options: {}".format(self._par['options'])
         print("{}, {}{}".format(key, t, o))
         
         d = self._par["description"]
         print("\t{}\n".format(d))


   _par = {
      "RefType" : {
         "options"    : ["none", "refro", "refco", "refcoq"],
         "description": "Computation method for atmospheric refraction",
         "type"       : str
      },
      "EopType" : {
         "options"    : ["2006", "2000B"],
         "description": "Type of Earth rotation model and corresponding Earth orientation parameters",
         "type"       : str
      },
      "TaiType" : {
         "options"    : ["instant", "scale"],
         "description": "UTC to TAI method",
         "type"       : str
      },
      "TtType" : {
         "options"    : ["BIPM", "TAI"],
         "description": "TAI to TT method",
         "type"       : str
      },
      "unit" : {
         "options"    : ["TCB", "TDB"],
         "description": "Output quantities compatible with TCB or TDB time standard",
         "type"       : str
      },
      "DE" : {
         "options"    : None,
         "description": "JPL ephemerides: 430, 430t, 438 etc.",
         "type"       : str
      },
      "TtTdbMethod" : {
         "options"    : ["eph", "FB01", "FBgeo"],
         "description": "TT to TDB method",
         "type"       : str
      },
      "SBscaling" : {
         "options"    : [False, True],
         "description": "Linear scaling between tB and tS due to relativistic effects",
         "type"       : bool
      },
      "PlanetShapiro" : {
         "options"    : [True, False],
         "description": "Planetary shapiro delay",
         "type"       : bool
      },
      "CompareT2" : {
         "options"    : [False, True],
         "description": "Calculate uSB using TEMPO2 method for comparison",
         "type"       : bool
      },
      "RVmethod" : {
         "options"    : ["analytical", "numerical"],
         "description": "The method used for RV modeling, numerical is used only for comparison",
         "type"       : str
      },
      "LenRVmethod" : {
         "options"    : ["T2", "PEXO"],
         "description": "The method used to derive RV lensing, T2 is used by default to be consistent with shapiro delay model in PEXO",
         "type"       : str
      },
      "BinaryModel" : {
         "options"    : ["none", "DDGR", "kepler"],
         "description": "Binary model",
         "type"       : str
      },
      "ellipsoid" : {
         "options"    : ["WGS84", "GRS80", "WGS72"],
         "description": "Ellipsoidal (normal) Earth Gravitational Model",
         "type"       : str
      },
      "epoch" : {
         "options"    : None,
         "description": "Epoch when the astrometry and position of the target is measured, JD or MJD",
         "type"       : numbers.Number
      },
      "observatory" : {
         "options"    : None,
         "description": "Observatory name, default CTIO",
         "type"       : str
      },
      "xtel" : {
         "options"    : None,
         "description": "Geocentric position (X) of the telescope in the International Terrestrial Reference Frame (ITRF), metres",
         "type"       : numbers.Number
      },
      "ytel" : {
         "options"    : None,
         "description": "Geocentric position (Y) of the telescope in the International Terrestrial Reference Frame (ITRF), metres",
         "type"       : numbers.Number
      },
      "ztel" : {
         "options"    : None,
         "description": "Geocentric position (Z) of the telescope in the International Terrestrial Reference Frame (ITRF), metres",
         "type"       : numbers.Number
      },
      "tdk" : {
         "options"    : None,
         "description": "Ambient temperature at the observer",
         "type"       : numbers.Number
      },
      "pmb" : {
         "options"    : None,
         "description": "Pressure at the telescope, millibar",
         "type"       : numbers.Number
      },
      "rh" : {
         "options"    : None,
         "description": "Relative humidity at the observer (range 0-1)",
         "type"       : numbers.Number
      },
      "wl" : {
         "options"    : None,
         "description": "effective wavelength of the source, micrometres",
         "type"       : numbers.Number
      },
      "tlr" : {
         "options"    : None,
         "description": "Temperature lapse rate in the troposphere, positive number",
         "type"       : numbers.Number
      },
      "g" : {
         "options"    : None,
         "description": "One of the PPN parameters, 1, 0 or any other values > 0",
         "type"       : numbers.Number
      },
      "mT" : {
         "options"    : None,
         "description": "Target mass, solar masses",
         "type"       : numbers.Number
      },
      "mC" : {
         "options"    : None,
         "description": "Companion mass, solar masses",
         "type"       : numbers.Number
      },
      "ra" : {
         "options"    : None,
         "description": "Right ascension (RA) of the barycenter (TSB), degrees",
         "type"       : numbers.Number
      },
      "dec" : {
         "options"    : None,
         "description": "Declination (DEC) of the barycenter (TSB), degrees",
         "type"       : numbers.Number
      },
      "plx" : {
         "options"    : None,
         "description": "Parallax of the barycenter (TSB), mas",
         "type"       : numbers.Number
      },
      "pmra" : {
         "options"    : None,
         "description": "Proper motion in RA of the barycenter (TSB), mas/yr",
         "type"       : numbers.Number
      },
      "pmdec" : {
         "options"    : None,
         "description": "Proper motion in DEC of the barycenter (TSB), mas/yr",
         "type"       : numbers.Number
      },
      "rv" : {
         "options"    : None,
         "description": "Radial velocity of the barycenter (TSB), km/s",
         "type"       : numbers.Number
      },
      "aT" : {
         "options"    : None,
         "description": "Semi-major axis of the barycentric motion of the target, au",
         "type"       : numbers.Number
      },
      "P" : {
         "options"    : None,
         "description": "Orbital period of the target, years",
         "type"       : numbers.Number
      },
      "e" : {
         "options"    : None,
         "description": "Eccentricity",
         "type"       : numbers.Number
      },
      "I" : {
         "options"    : None,
         "description": "Inclination, degrees",
         "type"       : numbers.Number
      },
      "omegaT" : {
         "options"    : None,
         "description": "Argument of periastron, degrees",
         "type"       : numbers.Number
      },
      "Omega" : {
         "options"    : None,
         "description": "Longitude of ascending node, degrees",
         "type"       : numbers.Number
      },
      "Tp" : {
         "options"    : None,
         "description": "Periastron epoch, JD or MJD",
         "type"       : numbers.Number
      }
   }