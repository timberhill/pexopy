import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import unittest
from pexopy import Pexo, FitOutput, EmulationOutput

class PexopyArgumentsTest(unittest.TestCase):

    def test_emulate_1(self):
        print("Running a test emulation, this should take <1min")
        output = Pexo(verbose=False).run(
            mode="emulate",
            primary="HD128621",
            ins="HARPS",
            time="2450000 2453000 10"
        )
        self.assertIsInstance(output, EmulationOutput)


    def test_fit_1(self):
        print("Running a test fit for HD239960, this should take <2min")
        output = Pexo(verbose=False).run(
            mode="fit",
            primary="HD239960",
            Niter=100,
            ncore=4
        )
        self.assertIsInstance(output, FitOutput)


if __name__ == "__main__":
    unittest.main()
