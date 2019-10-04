from pexopy import Pexo

tauCeti = {
    "mode" : "emulate",
    "c"    : "TR",
    "time" : "../pexo/input/mjd42000to52000by10day.tim",
    "par"  : "../pexo/input/TC_Fig11b.par"
}

alphaCen = {
    "mode" : "emulate",
    "c"    : "TA",
    "time" : "../pexo/input/gaia80yrby10day.tim",
    "par"  : "../pexo/input/ACAgaia.par"
}


result = Pexo().run(alphaCen)

print("RESULT : ", result)
