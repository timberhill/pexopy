import numpy as np
import matplotlib.pyplot as plt
import barycorrpy
from astropy.time import Time


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
# take = 10000
# JDUTC = JDUTC[:take]
# BJDTDB_pexo = BJDTDB_pexo[:take]
# done


BJDTDB_barycorrpy = barycorrpy.utc_tdb.JDUTC_to_BJDTDB(
    JDUTC,
    hip_id=8102,
    lat=-30.169283,
    longi=-70.806789,
    alt=2241.9
)[0]

# BRV_barycorrpy = barycorrpy.get_BC_vel(
#     JDUTC=JDUTC,
#     ra=026.021364597,
#     dec=-15.93955572,
#     obsname="",
#     lat=-30.1692833,
#     longi=-70.80678842222223,
#     alt=2241.8748,
#     epoch=2448349.0625,
#     pmra=-1721.05,
#     pmdec=854.16,
#     px=273.96,
#     rv=-16.68,
#     zmeas=0.0,
#     ephemeris="https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de405.bsp",
#     leap_update=True
# )[0]


# save the data
np.savetxt("PEXOvsBarycorrpy.csv", np.array([JDUTC, BJDTDB_pexo, BJDTDB_barycorrpy]).T,
    delimiter="\t", header="JDUTC\tBJDTDB_pexo\tBJDTDB_barycorrpy")

# PLOT
f, ax = plt.subplots(2, 1, sharex=True, figsize=(12,9))

ax[0].scatter(JDUTC, seconds_per_day * (BJDTDB_pexo       - JDUTC), marker="o", facecolors="none", edgecolors="k", label="PEXO")
ax[0].scatter(JDUTC, seconds_per_day * (BJDTDB_barycorrpy - JDUTC), marker="+", color="b", label="barycorrpy")
ax[0].set_xlabel("JDUTC, days")
ax[0].set_ylabel("BJDTDB - JDUTC, seconds")
ax[0].legend(loc="upper right")

ax[1].plot(JDUTC, ms_per_day * (BJDTDB_pexo - BJDTDB_barycorrpy), "k-", label="PEXO - barycorrpy")
ax[1].set_xlabel("JDUTC, days")
ax[1].set_ylabel("BJDTDB[PEXO] - BJDTDB[barycorrpy], ms")
ax[1].legend(loc="lower right")

# show "spikes" locations
mask = (ms_per_day * (BJDTDB_pexo - BJDTDB_barycorrpy)) < -850
spikejds = JDUTC[mask]
print("Spike locations:")
for i, jd in enumerate(spikejds):
    print(jd)
    ax[1].text(jd+10, -900 + i*50, str(jd), color="r")

plt.savefig("PEXOvsBarycorrpy.pdf")
plt.show()


np.savetxt(
    "PEXOvsBarycorrpy.csv",
    np.array([
        JDUTC,
        BJDTDB_pexo,
        BJDTDB_barycorrpy
    ]).T,
    delimiter="\t",
    header="JDUTC\tBJDTDB_pexo\tBJDTDB_barycorrpy"
)

