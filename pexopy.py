import os
import subprocess

import helpers


class Pexo(object):
    """
    PEXO wrapper class
    """
    def __init__(self, suppress_output=False):
        # ensure R dependencies are installed
        helpers.check_dependencies()

        # test paths
        # self.pexopath = "/home/timberhill/soft/pexo_test/code/"
        self.pexo_main = "/home/timberhill/soft/pexo_test/code_v3/binary_test.R"

        # get R path used in rpy2
        self.Rscript = "{}/{}".format(os.environ["R_HOME"], "bin/Rscript")

        self.suppress_output = suppress_output
        self.original_directory = os.getcwd()  # if needed?


    def run(self, binary_model="DDGR", observatory=None, astrometry=None, binary=None):
        """
        run PEXO
        """
        self._validate_parameters(binary_model, observatory, astrometry, binary)

        # see if you need output
        if self.suppress_output:
            stderr = None
        else:
            stderr = open('/dev/null', 'w')

        # TODO : handle file/string/dictionary types
        # assume args are strings
        args = [binary_model, observatory, astrometry, binary]
        cmd = [self.Rscript, self.pexo_main] + args

        print("\n\nEXECUTING\n", " ".join(cmd))

        # RUN PEXO
        result = subprocess.check_output(cmd, universal_newlines=True, stderr=stderr)

        # TODO : get the output files, turn them into objects?
        return result
        

    def _validate_parameters(self, binary_model, observatory, astrometry, binary):
        # TODO : allow for file object, file paths and dictionaries

        if binary_model not in ["kepler", "DD", "DDGR"]:
            raise ValueError("Parameter 'binary_model' in Pexo.run() must be one of the following: 'kepler', 'DD', or 'DDGR'.")

        if not isinstance(observatory, str):
            raise NotImplementedError('validation is not implemented yet')
