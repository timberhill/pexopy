import os
import re
from subprocess import Popen, PIPE, call, check_output
from datetime import datetime
from .settings import out_storage, par_storage, tim_storage
from .pexopar import PexoPar
from .pexotim import PexoTim
from .pexoout import PexoOut


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/
    """
    def __init__(self):
        self.setup()
        self.cwd = os.getcwd() # current directory
    

    def _print(self, message, verbose=True):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[0:10]
        if verbose:
            # print(f"[{timestamp}] {str(message)}") # python 3+
            print("[{}] {}".format(timestamp, str(message))) # python 2.7


    def setup(self, Rscript=None, pexodir=None, verbose=False):
        """
        Set up the wrapper.

        `Rscript`, str: path to Rscript, optional

        `pexodir`, str: path to PEXO repository, optional if $PEXODIR environment variable is installed.
        """
        # Find and validate Rscript

        if Rscript is None: # find Rscript
            with open(os.devnull, 'w') as FNULL:
                rc = call(['which', 'Rscript'], stdout=FNULL)
            if rc == 0: # 'which' found the path
                self.Rscript = check_output("which Rscript", shell=True).decode("ascii").strip()
            else: # 'which' returned an error
                raise OSError("Could not find Rscript. Make sure it's installed correctly or specify the path to it in Pexo.setup(Rscript=)")
        else: # use the path provided by user
            if os.path.exists(Rscript) and Rscript.endswith("Rscript"): # success
                self.Rscript = Rscript
            else:
                raise OSError("Specified Rscript path is not valid.")

        # self._print(f"Found Rscript at {self.Rscript}", verbose=verbose) # python 3+
        self._print("Found Rscript at {}".format(self.Rscript), verbose=verbose) # python 2.7

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
            
        # self._print(f"Found PEXO at    {self.pexodir}", verbose=verbose) # python 3+
        self._print("Found PEXO at    {}".format(self.pexodir), verbose=verbose) # python 2.7

        self.pexo_main    = os.path.join(self.pexodir, "code/pexo.R")
        self.pexodir_code = os.path.join(self.pexodir, "code")


    def _validate_parameter(self, name, value):
        known_commands = ["mode", "m", "component", "c", "time", "t", "par", "p", "var", "v", "out", "o", "figure", "f"]
        if name not in known_commands:
            # errormessage = f"Unknown parameter name: '{name}'." # python 3+
            errormessage = "Unknown parameter name: '{}'.".format(name) # python 2.7
            raise ValueError(errormessage)

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
        command = [self.Rscript, "pexo.R"]
        for key in params:
            if params[key] is not None:
                # name = f"-{key}" if len(key) == 1 else f"--{key}" # python 3+
                name = "-"+key if len(key) == 1 else "--"+key # python 2.7
                command.append(name)
                command.append(str(params[key]))

        return command


    def run(self, mode="emulate", component="TAR", time=None, par=None, var=None, out=None, verbose=True):
        """
        Run PEXO.

        `mode`, str: PEXO mode, `emulate` or `fit` [optional; default=emulate].

        `component`, str: PEXO model component: timing (T), astrometry (A), radial velocity (R) and their combinations [optional; default='TAR'].

        `time`, str/array/tuple/PexoTim: Four options are possible: 1. Timing file path with epochs/times in 1-part or 2-part JD[UTC] format; 2. Array/list of 1-part or 2-part JD[UTC], with a shape (N,1) or (N,2); 3. Tuple with floats/ints like (from, to, step); 4. PexoTim object [mandatory if mode='emulate'].

        `par`, str/dict/PexoPar: Parameters for models, observatory, for Keplerian/binary motion etc. The value must be a parameter file path, a dictionary with the parameters or a PexoPar object . Refer to the documentation for the full list [mandatory].

        `var`, str/array_like: Output variables as an array/list or space-separated string. Refer to the documentation for the full list [optional; default=None].

        `out`, str: Output file name: relative or absolute path [optional].

        Returns:

        <class 'numpy.ndarray'>, a table with the output variables (default or the ones specified in the `var` argument).
        """
        if mode == "fit":
            raise NotImplementedError("Fitting mode is not yet implemented, but it's coming soon.")

        # --time is mandatory for emulation
        if mode == "emulate" and time is None:
            raise ValueError("The `time` argument is mandatory for emulation.")
        
        if par is None:
            raise ValueError("The `par` argument is mandatory.")

        # output parameters, list -> str
        if isinstance(var, list) or 'array' in str(type(var)):
            var = " ".join(var)

        # read/generate/validate input files
        self.par = PexoPar(par)
        self.pararg = os.path.relpath(self.par.path,  start=self.pexodir_code)
        if type(time) == tuple and len(time) == 3:
            # self.timearg = f"{time[0]} {time[1]} {time[2]}" # python 3+
            self.timearg = "{} {} {}".format(time[0], time[1], time[2]) # python 2.7
        else:
            self.time = PexoTim(time)
            self.timearg = os.path.relpath(self.time.path, start=self.pexodir_code)
        
        # set up output handling
        if out is None:
            if type(time) == tuple and len(time) == 3:
                tail_tim = "-".join(str(t).replace(".", "_") for t in time)
            else:
                tail_tim = os.path.basename(self.time.path).replace(".tim", "")
            tail_par = os.path.basename(self.par.path).replace(".par", "")
            # self.out = os.path.relpath(os.path.join(out_storage, f"{tail_par}-{tail_tim}.out"), start=self.pexodir_code) # python 3+
            self.out = os.path.relpath(os.path.join(out_storage, "{}-{}.out".format(tail_par, tail_tim)), start=self.pexodir_code) # python 2.7
        else:
            self.out = os.path.relpath(out, start=self.pexodir_code)
            
        # collect the parameters
        params = {
            "m" : mode,
            "c" : component,
            "t" : self.timearg,
            "p" : self.pararg,
            "v" : var,
            "o" : self.out,
            "f" : "FALSE" # suppress plotting
        }

        # validate the parameters
        for param in params:
            self._validate_parameter(param, params[param])

        cmd = self._construct_command(params)

        # RUN PEXO
        os.chdir(os.path.join(self.pexodir, "code")) # go to pexo code directory

        self._print("Running PEXO with:\n$ " + " ".join(cmd) + "\n", verbose=verbose)

        if verbose:
            rc = call(cmd)
        else:
            with open(os.devnull, "w") as FNULL:
                rc = call(cmd, stdout=FNULL, stderr=FNULL)

        if rc != 0:
            # errormessage = f"Underlying PEXO code return non-zero exit status {rc}." # python 3+
            errormessage = "Underlying PEXO code return non-zero exit status {}.".format(rc) # python 2.7
            raise ChildProcessError()

        self._print("Done.", verbose=verbose)

        output = PexoOut().read(self.out)

        os.chdir(self.cwd)
        return output
    

    def clear_cache(self, verbose=True):
        count = 0
        for folder in [par_storage, tim_storage, out_storage]:
            filenames = os.listdir(folder)
            for filename in filenames:
                os.remove(os.path.join(folder, filename))
                count += 1
        
        if verbose:
            # self._print(f"{count} files removed.", verbose=verbose) # python 3+
            self._print("{} files removed.".format(count), verbose=verbose) # python 2.7
