import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

abl = camp(R22, "abl")
ctl = camp(R22, "ctl")
orig = camp(R11, "orig")
print("ERROR abl:", [e for _, e in abl])
# la fila ERROR de abl_s2 (c1_150_5) se reejecuto aparte con el mismo binario y semilla (abl_s2_rerun_c1_150_5.csv)
rr, _ = load(find("abl_s2_rerun_c1_150_5.csv"))
for k, v in rr.items():
    abl[1][0][k] = v
print("reejecucion integrada:", list(rr))
cf = ["ConsK2", "ConsK1", "Swo", "SwoNoLearn", "Milp", "Harvest"]
I = common([abl], [cf])
print("instancias comunes abl:", len(I), "(se excluye la instancia con ERROR en alguna semilla)")
lab = {"ConsK2": "Construccion k=2", "ConsK1": "Construccion k=1", "Swo": "SWO T=20", "SwoNoLearn": "SWO sin aprendizaje (rho=0)", "Milp": "+ recombinacion (MILP 60)", "Harvest": "+ harvest (=Balanced)"}
for c in cf: line(lab[c], abl, c, I)
print("-- comparaciones --")
cmp(abl, "ConsK1", abl, "ConsK2", I, "k=1 - k=2 (construccion)")
cmp(abl, "Swo", abl, "ConsK2", I, "SWO T=20 - construccion k=2")
cmp(abl, "SwoNoLearn", abl, "Swo", I, "SWO sin aprend. - SWO")
cmp(abl, "Milp", abl, "Swo", I, "Milp - SWO T=20")
cmp(abl, "Harvest", abl, "Milp", I, "Harvest - Milp")
cmp(abl, "Harvest", abl, "Swo", I, "Harvest - SWO T=20")
# control SWO a igual tiempo = ctl SwoT26 (otra campana, mismo protocolo): sobre las mismas instancias
I2 = common([abl, ctl], [cf, ["SwoT26"]])
print("-- control a igual tiempo (ctl SwoT26, T=26, 24.3 s) en %d instancias comunes --" % len(I2))
line("ctl SWO T=26", ctl, "SwoT26", I2); line("Milp (abl)", abl, "Milp", I2); line("Harvest (abl)", abl, "Harvest", I2)
cmp(abl, "Milp", ctl, "SwoT26", I2, "Milp - ctl SWO T=26"); cmp(abl, "Harvest", ctl, "SwoT26", I2, "Harvest - ctl SWO T=26")
cmp(ctl, "SwoT26", abl, "Swo", I2, "ctl SWO T26 - abl SWO T20")
print("-- MILP --")
for c in ["Milp", "Harvest"]:
    n, imp, lp, pr, tm = milp_stats(abl, c, I)
    print("  %-8s n=%d mejoran %d (%.1f%%) LP prueba %d probado %d t_milp %.1f" % (c, n, imp, 100 * imp / n, lp, pr, tm))
print("  SWO antes del MILP (Harvest): ", np.mean(tots(abl, "Harvest", I, key="swo")), " (Milp):", np.mean(tots(abl, "Milp", I, key="swo")))
print("-- ablacion de la nube (Linux, tab_ablation.tex, 3 sem., 240 inst., T medido con clock()=CPU): 7383.3 / 7594.0 / 7272.3 / 7306.3 / T26 7270.7 / recomb 7256.3 / harvest 7254.0")

print("\n\n===== SENSIBILIDAD (72 originales, 3 semillas, base = Fast) =====")
sens = camp(R22, "sens")
print("ERROR sens:", [e for _, e in sens])
d0 = sens[0][0]
names = [c[:-5] for c in next(iter(d0.values())).keys() if False] or [k for k in next(iter(d0.values())).keys() if k != "lb"]
Is = common([sens], [names])
print("instancias:", len(Is), " configs:", names)
base = tots(sens, "Base", Is)
print("  %-12s %-18s %8s %6s %8s  %s" % ("config", "totales/semilla", "media", "sd", "t medio", "dif vs Base (mejor/peor sobre medias, p)"))
for c in names:
    t = tots(sens, c, Is); tm = tmean(sens, c, Is)
    ma = [np.mean([d[i][c]["bins"] for d, _ in sens]) for i in Is]; mb = [np.mean([d[i]["Base"]["bins"] for d, _ in sens]) for i in Is]
    p = wp(ma, mb); b = sum(x < y for x, y in zip(ma, mb)); w = sum(x > y for x, y in zip(ma, mb))
    print("  %-12s %-18s %8.1f %6.1f %8.1f  %+6.1f (%d/%d, p=%.3g)" % (c, "/".join(map(str, t)), np.mean(t), sd(t), tm[0], np.mean(t) - np.mean(base), b, w, p))

