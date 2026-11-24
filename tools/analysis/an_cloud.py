import os
import sys, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
# ablacion de la nube (Linux): totales por config/semilla y comparacion pareada con la nuestra
cl = collections.defaultdict(dict)
with open(os.path.join(REPO, "results", "bpp", "ablation_2026-11", "runs.csv"), newline="") as fh:
    for r in csv.DictReader(fh):
        cl[(r["config"], int(r["seed"]))][r["instance"]] = (int(r["bins"]), float(r["time"]), r["valid"])
abl = camp(R22, "abl")
rr, _ = load(find("abl_s2_rerun_c1_150_5.csv"))
for k, v in rr.items(): abl[1][0][k] = v
cf = ["ConsK2", "ConsK1", "Swo", "SwoNoLearn", "Milp", "Harvest"]
mp = {"ConsK2": "constr_k2", "ConsK1": "constr_k1", "Swo": "swo", "SwoNoLearn": "swo_rho0", "Milp": "recomb", "Harvest": "harvest"}
I = common([abl], [cf])
print("instancias nuestras:", len(I))
print("%-12s %-22s %-8s %-8s | %-22s %-8s %-8s | dif medio (nuestra - nube)" % ("config", "nuestra por semilla", "media", "t medio", "nube por semilla", "media", "t medio"))
for c in cf + ["swo_T26"]:
    if c in mp:
        ours = tots(abl, c, I); to = tmean(abl, c, I)[0]; key = mp[c]
    else:
        ours = None; key = "swo_T26"
    cloud = [sum(cl[(key, s)][i][0] for i in I) for s in (1, 2, 3)]
    tc = np.mean([cl[(key, s)][i][1] for s in (1, 2, 3) for i in I])
    if ours:
        print("%-12s %-22s %-8.1f %-8.1f | %-22s %-8.1f %-8.1f | %+.1f" % (c, "/".join(map(str, ours)), np.mean(ours), to, "/".join(map(str, cloud)), np.mean(cloud), tc, np.mean(ours) - np.mean(cloud)))
    else:
        print("%-12s %-22s %-8s %-8s | %-22s %-8.1f %-8.1f" % ("swo_T26 nube", "-", "-", "-", "/".join(map(str, cloud)), np.mean(cloud), tc))
# invalidas en la nube
inv = sum(1 for (k, s), d in cl.items() for i, v in d.items() if str(v[2]) != str(v[0]))
print("filas de la nube con valid != bins:", inv)
# pares dentro de nuestra ablacion sobre las 240
print("\nNuestra ablacion sobre %d instancias (con la reejecucion):" % len(I))
for c in cf: line(c, abl, c, I)
cmp(abl, "Milp", abl, "Swo", I, "Milp - SWO T=20")
cmp(abl, "Harvest", abl, "Milp", I, "Harvest - Milp")
cmp(abl, "SwoNoLearn", abl, "Swo", I, "SWO sin aprend. - SWO")
cmp(abl, "ConsK1", abl, "ConsK2", I, "k=1 - k=2")
cmp(abl, "Swo", abl, "ConsK2", I, "SWO T=20 - construccion")
ctl = camp(R22, "ctl")
I2 = common([abl, ctl], [cf, ["SwoT26"]])
cmp(abl, "Milp", ctl, "SwoT26", I2, "Milp - ctl SWO T=26")
cmp(abl, "Harvest", ctl, "SwoT26", I2, "Harvest - ctl SWO T=26")
print("  ctl SwoT26:", tots(ctl, "SwoT26", I2), np.mean(tots(ctl, "SwoT26", I2)))

