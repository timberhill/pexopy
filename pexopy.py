import os
import subprocess

# import helpers


class Pexo(object):
    """
    A Python wrapper for PEXO - https://github.com/phillippro/pexo/


    """
    def __init__(self):
        self.setup()

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
        if \
            not os.path.exists(self.pexodir) or \ 
            not os.path.exists(os.path.join(self.pexodir, "code")) or \
            not os.path.isfile(os.path.join(self.pexodir, "code/pexo.R")):
            raise OSError("The PEXO directory specified is not valid.")
            

        self.pexo_main = os.path.join(self.pexodir, "code/pexo.R")


    def _get_last_output(self):
        """
        Get
        """
        raise NotImplementedError("Pexo._get_last_output() is not yet implemented.")


    def run(self, binary_model="DDGR", observatory=None, astrometry=None, binary=None):
        """
        Run PEXO
        """
        self._validate_parameters(binary_model, observatory, astrometry, binary)

        # go to pexo directory
        os.chdir(os.path.join(self.pexodir, "code"))

        # see if you need output
        # if self.suppress_output:
        #     stderr = None
        # else:
        #     stderr = open('/dev/null', 'w')
        stderr = open('/dev/null', 'w')
        stdout = subprocess.STDOUT

        # TODO : handle file/string/dictionary types
        # assume args are strings
        args = [binary_model, observatory, astrometry, binary]
        cmd = [self.Rscript, self.pexo_main] + args

        print("\n\nEXECUTING\n", " ".join(cmd))

        # RUN PEXO
        result = subprocess.check_output(cmd, universal_newlines=True)

        # go back to the original directory
        os.chdir(self.cwd)

        # TODO : get the output files, turn them into objects?
        return result
        

    def _validate_parameters(self, binary_model, observatory, astrometry, binary):
        # TODO : allow for file object, file paths and dictionaries

        if binary_model not in ["kepler", "DD", "DDGR"]:
            raise ValueError("Parameter 'binary_model' in Pexo.run() must be one of the following: 'kepler', 'DD', or 'DDGR'.")

        if not isinstance(observatory, str):
            raise NotImplementedError('validation is not implemented yet')

Pexo()