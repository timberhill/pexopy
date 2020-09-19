import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import unittest
from pexopy import Pexo

class PexopyArgumentsTest(unittest.TestCase):
    def test_fit_no_error(self):
        print("Running a test fit, this should take <2min")
        output = Pexo(verbose=False).run(
            mode="fit",
            primary="HD239960",
            Niter=100,
            ncore=4
        )
        self.assertIsNotNone(output)


if __name__ == '__main__':
    unittest.main()
