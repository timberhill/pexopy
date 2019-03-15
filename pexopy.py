import os
import subprocess

# import helpers


class Pexo(object):
    """
    PEXO wrapper class
    """
    def __init__(self):
        self.R       = subprocess.check_output("which R", shell=True).decode("ascii").strip()
        self.Rscript = subprocess.check_output("which Rscript", shell=True).decode("ascii").strip()
        self.pexodir = subprocess.check_output("echo $PEXODIR", shell=True).decode("ascii").strip()

        self.pexo_main = "{}/{}".format(self.pexodir, "code/binary_test.R").replace("//", "/")

        self.cwd = os.getcwd() # current directory
        

    def _get_last_output(self):
        raise NotImplementedError("Pexo._get_last_output() is not yet implemented.")


    def run(self, binary_model="DDGR", observatory=None, astrometry=None, binary=None):
        """
        run PEXO
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
