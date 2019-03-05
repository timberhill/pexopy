import os

import rpy2.rinterface
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector


# R packages to install if missing
R_dependencies = ["gmp"]#, "Rmpfr"]


def check_dependencies():
    utils = rpackages.importr('utils')

    # Selectively install what needs to be install.
    # package 'gmp' needs this: https://gmplib.org/manual/Installing-GMP.html
    to_install = [x for x in R_dependencies if not rpackages.isinstalled(x)]

    if len(to_install) > 0:
        print("The following packages need to be installed: ", to_install)
        utils.chooseCRANmirror(ind=1)  # select the first mirror in the list
        utils.install_packages(StrVector(to_install))
    else:
        print("All R dependencies are installed.")
