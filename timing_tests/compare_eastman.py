import numpy as np
import matplotlib.pyplot as plt




minutes_per_day = 1440
seconds_per_day = minutes_per_day * 60
ms_per_day = seconds_per_day * 1000


# PEXO
pexo_output = np.genfromtxt(
    "ddt_TC_timing_DDGR_dt10day_Ntime400.csv",
    delimiter="\t",
    skip_header=2
).T

JDUTC_pexo  = np.array([pexo_output[0], pexo_output[1]])
MJDUTC = [x[0]-2400000.5 + x[1] for x in JDUTC_pexo.T]
BJDTDB_pexo = np.array([pexo_output[2], pexo_output[3]])
BJDTDB_correction_pexo = pexo_output[3] - pexo_output[1]


# EASTMAN
# code: http://astroutils.astronomy.ohio-state.edu/time/
# online tool: http://astroutils.astronomy.ohio-state.edu/time/utc2bjd.html
eastman_output = np.genfromtxt(
    "eastman.dat",
    delimiter="\t",
    skip_header=1
).T

MJDUTC = eastman_output[0]
BJDTDB_eastman = eastman_output[1]

# PLOT
f, ax = plt.subplots(2, 1, sharex=True, figsize=(12,9))

ax[0].scatter(MJDUTC, seconds_per_day * (BJDTDB_pexo[1] - JDUTC_pexo[1]), marker="o", facecolors="none", edgecolors="k", label="PEXO")
ax[0].scatter(MJDUTC, seconds_per_day * (BJDTDB_eastman  - MJDUTC), marker="+", color="b", label="Eastman2010")
ax[0].set_xlabel("JDUTC, days")
ax[0].set_ylabel("BJDTDB - JDUTC, seconds")
ax[0].legend(loc="upper right")

diff = ms_per_day * (BJDTDB_correction_pexo - BJDTDB_eastman + MJDUTC)
ax[1].plot(MJDUTC, diff, "k-", label="PEXO - Eastman2010")
ax[1].set_xlabel("JDUTC, days")
ax[1].set_ylabel("BJDTDB[PEXO] - BJDTDB[Eastman2010], ms")
ax[1].legend(loc="upper right")

# show "spikes" locations
# spikejds = MJDUTC[diff > 1]
# print("Spike locations:")
# for i, jd in enumerate(spikejds):
#     print(jd)
#     ax[1].text(jd+10, 1 + i*1, str(jd), color="r")

plt.savefig("PEXOvsEastman2010.pdf")
plt.show()

exit()
np.savetxt(
    "PEXOvsEastman2010.csv",
    np.array([
        JDUTC,
        BJDTDB_pexo,
        BJDTDB_barycorrpy
    ]).T,
    delimiter="\t",
    header="JDUTC\tBJDTDB_pexo\tBJDTDB_eastman"
)
