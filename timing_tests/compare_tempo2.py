import numpy as np
import matplotlib.pyplot as plt
import barycorrpy
from astropy.time import Time



def generate_tim(jds, split=10000000000):
    n = len(jds)
    i = 0
    jds_split = jds[ 0 : split ]
    while len(jds_split) > 0:
        filename = "tc.tim"
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
    "/home/timberhill/repositories/pexo/results/TC_timing_DDGR_dt10day_Ntime400.csv",
    delimiter="\t",
    skip_header=1
).T

JDUTC = pexo_output[0] + pexo_output[1]
BJDTDB_pexo = pexo_output[2] + pexo_output[3]


# take first 10000 points
# take = 1000
# JDUTC = JDUTC[:take]
# BJDTDB_pexo = BJDTDB_pexo[:take]
# done


# generate .tim file for tempo2
# generate_tim(JDUTC-2400000.5, split=10001)


tempo2_output = np.genfromtxt(
    "output100k.dat",
    delimiter=" ",
    skip_header=0
).T


BJDTDB_tempo2 = tempo2_output[1] + 2400000.5

# PLOT
f, ax = plt.subplots(2, 1, sharex=True, figsize=(12,9))

ax[0].scatter(JDUTC, seconds_per_day * (BJDTDB_pexo       - JDUTC), marker="o", facecolors="none", edgecolors="k", label="PEXO")
ax[0].scatter(JDUTC, seconds_per_day * (BJDTDB_tempo2 - JDUTC), marker="+", color="b", label="tempo2")
ax[0].set_xlabel("JDUTC, days")
ax[0].set_ylabel("BJDTDB - JDUTC, seconds")
ax[0].legend(loc="upper right")

ax[1].plot(JDUTC, ms_per_day * (BJDTDB_pexo - BJDTDB_tempo2), "k-", label="PEXO - tempo2")
ax[1].set_xlabel("JDUTC, days")
ax[1].set_ylabel("BJDTDB[PEXO] - BJDTDB[tempo2], ms")
ax[1].legend(loc="upper right")

# show "spikes" locations
mask = (ms_per_day * (BJDTDB_pexo - BJDTDB_tempo2)) > 1
spikejds = JDUTC[mask]
print("Spike locations:")
for i, jd in enumerate(spikejds):
    print(jd)
    ax[1].text(jd+10, 1 + i*1, str(jd), color="r")

plt.savefig("PEXOvsTempo2.pdf")
plt.show()


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


