from pexopy import Pexo

result = Pexo().run(
    binary_model="DDGR",
    observatory= "~/soft/pexo_test/code_v3/observatory.par",
    astrometry=  "~/soft/pexo_test/code_v3/astrometry_AC.par",
    binary=      "~/soft/pexo_test/code_v3/kepler_AC.par"
)

print("RESULT : ", result)
