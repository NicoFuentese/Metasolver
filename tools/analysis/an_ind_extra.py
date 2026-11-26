"""Industrial (Instance_CG, n >= 500): tiempo por contenedor y kappa al mismo tiempo (ind_kappa) y criterios de apoyo (ind_support).

ind_kappa: construccion sola con apoyo >= 70 %; T = kappa 1, tau 2 s; D = kappa 2, tau 0.02 s (defecto de MPV); E = kappa 2, tau 2 s.
ind_support: construccion sola kappa 1, tau 2 s con apoyo ninguno / 50 % / 70 % / 85 % / completo; ademas estadisticas de apoyo de las soluciones
(requiere las soluciones conservadas: <campana>_s<semilla>_sol/). Usa las semillas disponibles. uso: python an_ind_extra.py"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: E402,F403
import support_stats  # noqa: E402


def seeds_of(name):
    return tuple(s for s in (1, 2, 3) if os.path.exists(find("%s_s%d.csv" % (name, s))) and os.path.getsize(find("%s_s%d.csv" % (name, s))) > 0)


def block(name, title, cfgs, labels, pairs):
    ss = seeds_of(name)
    if not ss:
        print("\n== %s: sin datos" % name); return None
    cp = camp(None, name, ss)
    I = common([cp], [cfgs])
    lb = sum(cp[0][0][i]["lb"] for i in I)
    print("\n== %s | %s | %d semillas, %d instancias, cota del solver (suma) %d" % (name, title, len(ss), len(I), lb))
    for c, l in zip(cfgs, labels):
        line(l, cp, c, I)
    for a, b, lab in pairs:
        cmp(cp, a, cp, b, I, lab)
    return cp, I


block("ind_kappa", "tiempo por contenedor y kappa (80 instancias)", ["T", "D", "E"], ["k1 t2", "k2 t0.02", "k2 t2"],
      [("T", "D", "T - D"), ("T", "E", "T - E"), ("E", "D", "E - D")])

crit = ["None", "A50", "A70", "A85", "Full"]
r = block("ind_support", "criterios de apoyo (80 instancias)", crit, ["ninguno", "50%", "70%", "85%", "completo"],
          [("A50", "A70", "50% - 70%"), ("None", "A70", "ninguno - 70%"), ("A85", "A70", "85% - 70%"), ("Full", "A70", "completo - 70%")])
if r:
    for s in seeds_of("ind_support"):
        sol_dir = os.path.join(os.path.dirname(find("ind_support_s%d.csv" % s)), "ind_support_s%d_sol" % s)
        print("\n-- apoyo de las soluciones, semilla %d" % s)
        for tag in crit:
            files = glob.glob(os.path.join(sol_dir, "*_%s.csv" % tag))
            tot = ssum = n70 = full = 0
            for f in files:
                t, ss_, a, b = support_stats.stats(f)
                tot += t; ssum += ss_; n70 += a; full += b
            if tot:
                print("   %-5s soluciones %3d  apoyo medio %.1f%%  cajas >=70%% %.1f%%  apoyo completo %.1f%%" % (tag, len(files), 100 * ssum / tot, 100 * n70 / tot, 100 * full / tot))
