import numpy as np
import matplotlib.pyplot as plt
import barycorrpy
from astropy.time import Time



def generate_tim(jds, split=10000000000):
    n = len(jds)
    i = 0
    jds_split = jds[ 0 : split ]
    while len(jds_split) > 0:
        filename = "tempo2_inputs/tc.tim"
        if i != 0:
            filename += str(i)
        
        ni = len(jds_split)
        tim_data = np.array([
            ni*["HD10700"],
            ni*[545000000],
            [str(x) for x in jds_split],
            ni*[10.0],
            ni*["ctio"]
        ]).T

        print("Writing {} lines to {} ...".format(len(jds_split), filename))
        np.savetxt(
            filename,
            tim_data,
            delimiter=" ",
            header="FORMAT 1",
            comments="",
            fmt="%s %s %s %s %s"
        )
        
        i += 1
        jds_split = jds[ i*split : (i+1)*split ]



minutes_per_day = 1440
seconds_per_day = minutes_per_day * 60
ms_per_day = seconds_per_day * 1000


pexo_output = np.genfromtxt(
    "/home/timberhill/repositories/pexo/results/ddt_TC_timing_DDGR_dt10day_Ntime400.csv",
    delimiter="\t",
    skip_header=1
).T

JDUTC_pexo  = np.array([pexo_output[0], pexo_output[1]])
MJDUTC = [x[0]-2400000.5 + x[1] for x in JDUTC_pexo.T]
BJDTDB_pexo = np.array([pexo_output[2], pexo_output[3]])
BJDTDB_correction_pexo = pexo_output[3] - pexo_output[1]


# take first 10000 points
# take = 1000
# JDUTC = JDUTC[:take]
# BJDTDB_pexo = BJDTDB_pexo[:take]
# done


# generate .tim file for tempo2
# JDUTC_pexo_str = ["{:5.20f}".format( x[0] - 2400000.5 + x[1]) for x in JDUTC_pexo.T]
# generate_tim(JDUTC_pexo_str, split=10001)
# exit()

tempo2_output = np.genfromtxt(
    "tempo210k.csv",
    delimiter=" ",
    skip_header=1
).T

# MJDUTC = tempo2_output[0]
BJDTDB_tempo2 = tempo2_output[5]

# PLOT
f, ax = plt.subplots(2, 1, sharex=True, figsize=(12,9))

ax[0].scatter(MJDUTC, seconds_per_day * (BJDTDB_pexo[1] - JDUTC_pexo[1]), marker="o", facecolors="none", edgecolors="k", label="PEXO")
ax[0].scatter(MJDUTC, seconds_per_day * (BJDTDB_tempo2  - MJDUTC), marker="+", color="b", label="tempo2")
ax[0].set_xlabel("JDUTC, days")
ax[0].set_ylabel("BJDTDB - JDUTC, seconds")
ax[0].legend(loc="upper right")

diff = ms_per_day * (BJDTDB_correction_pexo - BJDTDB_tempo2 + MJDUTC)
ax[1].plot(MJDUTC, diff, "k-", label="PEXO - tempo2")
ax[1].set_xlabel("JDUTC, days")
ax[1].set_ylabel("BJDTDB[PEXO] - BJDTDB[tempo2], ms")
ax[1].legend(loc="upper right")

# show "spikes" locations
# spikejds = MJDUTC[diff > 1]
# print("Spike locations:")
# for i, jd in enumerate(spikejds):
#     print(jd)
#     ax[1].text(jd+10, 1 + i*1, str(jd), color="r")

plt.savefig("PEXOvsTempo2.pdf")
plt.show()

exit()
np.savetxt(
    "PEXOvsTempo2.csv",
    np.array([
        JDUTC,
        BJDTDB_pexo,
        BJDTDB_barycorrpy
    ]).T,
    delimiter="\t",
    header="JDUTC\tBJDTDB_pexo\tBJDTDB_tempo2"
)


