import os
import re
from subprocess import Popen, PIPE, call, check_output
from datetime import datetime
from .pexopar import PexoPar
from .pexotim import PexoTim
from .pexoout import PexoOutput
from .pexo_parameter import PexoParameters


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/
    """
    def __init__(self, Rscript=None, pexodir=None, verbose=False):
        self.setup(Rscript, pexodir, verbose)


    def setup(self, Rscript=None, pexodir=None, verbose=False):
        """
        Set up the wrapper.

        `Rscript`, str: path to Rscript, optional

        `pexodir`, str: path to PEXO repository, optional if $PEXODIR environment variable is installed.
        """
        self.cwd     = os.getcwd() # current directory
        self.verbose = verbose

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
            
        self._print("Found PEXO at    {}".format(self.pexodir), verbose=self.verbose)

        self.pexo_main    = os.path.join(self.pexodir, "code/pexo.R")
        self.pexodir_code = os.path.join(self.pexodir, "code")


    def run(self, **params):
        """
        Run PEXO.
        """
        parameters = PexoParameters(params)
        command = "{} pexo.R {}".format(self.Rscript, str(parameters))

        # RUN PEXO
        self._print("Running PEXO with:\n$ " + " ".join(command) + "\n", verbose=verbose)
        os.chdir(os.path.join(self.pexodir, "code")) # go to pexo code directory

        if self.verbose:
            rc = call(command)
        else:
            with open(os.devnull, "w") as FNULL:
                rc = call(command, stdout=FNULL, stderr=FNULL)

        if rc != 0:
            errormessage = "Underlying PEXO code return non-zero exit status {}.".format(rc)
            raise ChildProcessError(errormessage)

        self._print("Done.", verbose=verbose)

        output = PexoOutput(self.out, utc=self.time.data)
        parameters.clear_cache()

        os.chdir(self.cwd)
        return output


    def _print(self, message, verbose=True):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[0:10]
        if verbose:
            print("[{}] {}".format(timestamp, str(message)))
