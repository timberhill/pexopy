import os
import re
import subprocess
import settings
from parsers import PexoPar, PexoTim, PexoOut


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/


    """
    def __init__(self, suppress_output=True):
        self.setup()
        self.suppress_output = suppress_output # TODO : actually suppress output
        self.cwd = os.getcwd() # current directory


    def setup(self, Rscript=None, pexodir=None):
        """
        Set up the wrapper.

        `Rscript`, str: path to Rscript, optional

        `pexodir`, str: path to PEXO repository, optional if $PEXODIR environment variable is installed.
        """
        # Find and validate Rscript

        if Rscript is None: # find Rscript
            rc = subprocess.call(['which', 'Rscript'], stdout=None)
            if rc == 0: # 'which' found the path
                self.Rscript = subprocess.check_output("which Rscript", shell=True).decode("ascii").strip()
            else: # 'which' returned an error
                raise OSError("Could not find Rscript. Make sure it's installed correctly or specify the path to it in Pexo.setup(Rscript=)")
        else: # use the path provided by user
            if os.path.exists(Rscript) and Rscript.endswith("Rscript"): # success
                self.Rscript = Rscript
            else:
                raise OSError("Specified Rscript path is not valid.")

        # Find and validate PEXO directory path

        if pexodir is None:
            if "PEXODIR" in os.environ: # check the PEXODIR environment variable
                self.pexodir = os.getenv("PEXODIR")
            else: # PEXODIR is not set
                raise OSError("PEXODIR environment variable is not set. Consider setting it or specifying it in Pexo.setup(pexodir=)")
        else:
            self.pexodir = pexodir

        # make sure this folder is legit
        if not os.path.exists(self.pexodir) or \
            not os.path.exists(os.path.join(self.pexodir, "code")) or \
            not os.path.isfile(os.path.join(self.pexodir, "code/pexo.R")):
            raise OSError("The PEXO directory specified is not valid.")
            
        self.pexo_main    = os.path.join(self.pexodir, "code/pexo.R")
        self.pexodir_code = os.path.join(self.pexodir, "code")


    def _validate_parameter(self, name, value):
        known_commands = ["mode", "m", "component", "c", "time", "t", "par", "p", "var", "v", "out", "o", "figure", "f"]
        if name not in known_commands:
            raise ValueError(f"Unknown parameter name: '{name}'.")

        if name in ["mode", "m"] and value is not None:
            if value not in ["emulate", "fit"]:
                raise ValueError("'mode' parameter should be either 'emulate' or 'fit'.")
        
        elif name in ["component", "c"] and value is not None:
            if not bool(re.match("^[TtAaRr]+$", value)):
                raise ValueError("'component' parameter should be timing (T), astrometry (A), radial velocity (R) and their combinations.")
        
        elif name in ["time", "t"]:
            pass # this is validated while parsing
        
        elif name in ["par", "p"]:
            pass # this is validated while parsing
        
        elif name in ["var", "v"] and value is not None:
            if type(value) != str:
                raise ValueError("'var' parameter should contain output variables.")
        
        elif name in ["out", "o"] and value is not None:
            if type(value) != str:
                raise ValueError("'out' parameter should contain a path to save the output to.")

        elif name in ["figure", "f"] and value is not None:
            if value not in ["TRUE", "FALSE"]:
                raise ValueError("'figure' parameter should be 'FALSE' or 'TRUE'.")


    def _construct_command(self, params):
        command = f"{self.Rscript} pexo.R"
        for key in params:
            if params[key] is not None:
                name = f"-{key}" if len(key) == 1 else f"--{key}"
                command += f" {name} {params[key]}"
        
        return command


    def run(self, mode="emulate", component="TAR", time=None, par=None, var=None, out=None):
        """
        Run PEXO.


        `mode`, str: PEXO mode, `emulate` or `fit` [optional; default=emulate].

        `component`, str: PEXO model component: timing (T), astrometry (A), radial velocity (R) and their combinations [optional; default='TAR'].

        `time`, str/array/tuple/PexoTim: Four options are possible: 1. Timing file path with epochs/times in 1-part or 2-part JD[UTC] format; 2. Array/list of 1-part or 2-part JD[UTC], with a shape (N,1) or (N,2); 3. Tuple with floats/ints like (from, to, step); 4. PexoTim object [mandatory if mode='emulate'].

        `par`, str/dict/PexoPar: Parameters for models, observatory, for Keplerian/binary motion etc. The value must be a parameter file path, a dictionary with the parameters or a PexoPar object . Refer to the documentation for the full list [mandatory].

        `var`, str/array_like: Output variables as an array/list or space-separated string. Refer to the documentation for the full list [optional; default=None].

        `out`, str: Output file name: relative or absolute path [optional].
        """

        # --time is mandatory for emulation
        if time == "emulate" and time is None: # TODO : handle the tuple time=(2465000, 2466000, 10) case
            raise ValueError("The `time` argument is mandatory for emulation.")
        
        if par is None:
            raise ValueError("The `par` argument is mandatory.")

        # output parameters, list -> str
        if isinstance(var, list) or 'array' in str(type(var)):
            var = " ".join(var)

        # read/generate/validate input files
        self.time = PexoTim(time)
        self.par = PexoPar(par)
        
        # set up output handling
        if out is None:
            tail_par = os.path.basename(self.par.path).replace(".par", "")
            tail_tim = os.path.basename(self.time.path).replace(".tim", "")
            self.out = os.path.relpath(os.path.join(settings.out_storage, f"{tail_par}-{tail_tim}.out"), start=self.pexodir_code)
        else:
            self.out = os.path.relpath(out, start=self.pexodir_code)

        # collect the parameters
        params = {
            "m" : mode,
            "c" : component,
            "t" : os.path.relpath(self.time.path, start=self.pexodir_code),
            "p" : os.path.relpath(self.par.path,  start=self.pexodir_code),
            "v" : var,
            "o" : self.out,
            "f" : "FALSE" # suppress plotting
        }

        print(self.out)

        # validate the parameters
        for param in params:
            self._validate_parameter(param, params[param])

        cmd = self._construct_command(params)
        print(f"\n{os.getcwd()}\n{cmd}\n")

        # RUN PEXO
        os.chdir(os.path.join(self.pexodir, "code")) # go to pexo code directory
        subprocess.check_output(cmd.split())
        output = PexoOut().read(self.out)
        os.chdir(self.cwd)
        # TODO : suppress the output

        return output



if __name__ == "__main__":
    raise Exception("Please import Pexo class to use it.")
