import os
import re
import subprocess

# import helpers


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/


    """
    def __init__(self):
        self.setup()
        self.suppress_output = True
        self.cwd = os.getcwd() # current directory


    def setup(self, Rscript=None, pexodir=None):
        """
        Set up the wrapper.

        Rscript, <str>: path to Rscript, optional

        pexodir, <str>: path to PEXO repository, optional if $PEXODIR environment variable is installed.
        """
        # Find and validate Rscript

        if Rscript is None: # find Rscript
            rc = subprocess.call(['which', 'Rscript'])
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
            
        self.pexo_main = os.path.join(self.pexodir, "code/pexo.R")


    def _validate_parameter(self, name, value):
        if name in ["mode", "m"]:
            if value not in ["emulate", "fit"]:
                raise ValueError("'mode' parameter should be either 'emulate' or 'fit'.")
        
        elif name in ["component", "c"]:
            if not bool(re.match("^[TtAaRr]+$", value)):
                raise ValueError("'component' parameter should be timing (T), astrometry (A), radial velocity (R) and their combinations.")
        
        elif name in ["time", "t"]:
            if not os.path.isfile(value):
                raise ValueError("'time' parameter should be either a path to a timing file: epochs or times could be in 1-part or 2-part JD[UTC] format, or a 'Start End By' format.")
        
        elif name in ["par", "p"]:
            if not os.path.isfile(value):
                raise ValueError("'par' parameter should be a path to a PEXO parameter file.")
        
        elif name in ["var", "v"]:
            if type(value) != str:
                raise ValueError("'var' parameter should contain output variables.")
        
        elif name in ["out", "o"]:
            if type(value) != str:
                raise ValueError("'out' parameter should contain a path to save he output to.")

        elif name in ["figure", "f"]:
            if type(value) != str:
                raise ValueError("'figure' parameter should be false or true.")

        else:
            raise ValueError(f"Unknown parameter name: '{name}'.")


    def _construct_command(self, params):
        command = f"{self.Rscript} pexo.R"
        for key in params:
            name = f"-{key}" if len(key) == 1 else f"--{key}"
            command += f" {name} {params[key]}"
        
        return command


    def run(self, params):
        """
        Run PEXO

        params, <dict>: a dictionary of parameters, e.g. { "mode": "emulate" }
        """
        # TODO : custom parameter

        # validate the parameters
        for key in params:
            self._validate_parameter(key, params[key])

        # go to pexo directory
        os.chdir(os.path.join(self.pexodir, "code"))

        cmd = self._construct_command(params)

        # RUN PEXO
        with open(os.devnull, 'w') as devnull:
            result = subprocess.check_output(cmd.split(), stderr=devnull)


        # TODO : read, parse the output, return it

        # go back to the original directory
        os.chdir(self.cwd)

        return result