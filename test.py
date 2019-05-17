from pexopy import Pexo

result = Pexo().run(
    binary_model="DDGR",
    observatory= "~/soft/pexo_test/code/observatory.par",
    astrometry=  "~/soft/pexo_test/code/astrometry_AC.par",
    binary=      "~/soft/pexo_test/code/kepler_AC.par"
)

print("RESULT : ", result)

# Rscript /home/timberhill/soft/pexo_test/code/binary_test.R DDGR ~/soft/pexo_test/code/observatory.par ~/soft/pexo_test/code/astrometry_AC.par ~/soft/pexo_test/code/kepler_AC.par
# Rscript pexo.R DDGR observatory.par astrometry_AC.par kepler_AC.par