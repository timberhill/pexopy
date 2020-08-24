import os
import re
from subprocess import Popen, PIPE, call, check_output
from datetime import datetime
from .settings import out_storage, par_storage, tim_storage
from .pexopar import PexoPar
from .pexotim import PexoTim
from .pexoout import PexoOutput


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/
    """
    def __init__(self, Rscript=None, pexodir=None, verbose=False):
        self.setup(Rscript, pexodir, verbose)
        self.cwd = os.getcwd() # current directory


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
            if os.path.exists(Rscript) and Rscript.endswith("Rscript"):
                self.Rscript = Rscript
            else:
                raise OSError("Specified Rscript path is not valid.")

        self._print("Found Rscript at {}".format(self.Rscript), verbose=verbose)

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
            
        self._print("Found PEXO at    {}".format(self.pexodir), verbose=verbose)

        self.pexo_main    = os.path.join(self.pexodir, "code/pexo.R")
        self.pexodir_code = os.path.join(self.pexodir, "code")


    def run(self, **params):
        """
        Run PEXO.
        """

        # TODO: add custom validation

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
            raise ChildProcessError(errormessage)

        self._print("Done.", verbose=verbose)

        output = PexoOutput(self.out, utc=self.time.data)

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
            self._print("{} files removed.".format(count), verbose=verbose)


    def _print(self, message, verbose=True):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[0:10]
        if verbose:
            print("[{}] {}".format(timestamp, str(message)))


    def _parameter_handler(self, key):
        handlers = [
            dict(variations=["m", "mode"],      handler=self._handle_parameter_mode),
            dict(variations=["i", "ins"],       handler=self._handle_parameter_mode),
            dict(variations=["N", "Niter"],     handler=self._handle_parameter_mode),
            dict(variations=["P", "Planet"],    handler=self._handle_parameter_mode),
            dict(variations=["O", "orbit"],     handler=self._handle_parameter_mode),
            dict(variations=["g", "geometry"],  handler=self._handle_parameter_mode),
            dict(variations=["n", "ncore"],     handler=self._handle_parameter_mode),
            dict(variations=["c", "component"], handler=self._handle_parameter_mode),
            dict(variations=["t", "time"],      handler=self._handle_parameter_mode),
            dict(variations=["p", "primary"],   handler=self._handle_parameter_mode),
            dict(variations=["s", "secondary"], handler=self._handle_parameter_mode),
            dict(variations=["M", "mass"],      handler=self._handle_parameter_mode),
            dict(variations=["d", "data"],      handler=self._handle_parameter_mode),
            dict(variations=["C", "companion"], handler=self._handle_parameter_mode),
            dict(variations=["v", "var"],       handler=self._handle_parameter_mode),
            dict(variations=["o", "out"],       handler=self._handle_parameter_mode),
            dict(variations=["f", "figure"],    handler=self._handle_parameter_mode),
            dict(variations=["V", "verbose"],   handler=self._handle_parameter_mode),
        ]

        for handler in handlers:
            if key in handler["variations"]:
                return handler["handler"]
        
        raise ValueError("Unknown parameter: {}".format(key))


    def _handle_parameters(self, pairs):
        if not isinstance(pairs, dict):
            pairs = dict(pairs)
        return dict([(pair[0], self._parameter_handler(key)(pairs[key])) for key in pairs])


    def _handle_parameter_mode(self, value):
        if value.lower() not in ["emulate", "fit"]:
            raise ValueError("Incorrect value for the 'mode' parameter: {}".format(value))
        return value.lower()
