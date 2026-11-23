#!/usr/bin/env python3
"""
Tabla de la ablacion (tab:e-ablation) desde los resultados crudos de run_ablation.sh.

Lee <dir>/runs.csv y escribe en la salida estandar la tabla LaTeX: total de contenedores por semilla, media,
tiempo medio por instancia y, para cada fila, la diferencia con la fila de referencia (instancias mejores y
peores y prueba de Wilcoxon de rangos con signo, bilateral, sobre las medias por instancia). Verifica antes que
todas las corridas esten completas y validas (bins == valid).
uso: table_ablation.py <dir> [--partial]   (--partial: usa solo las instancias completas en todas las filas)
"""
import csv
import math
import sys
from collections import defaultdict

# filas: (config, etiqueta, referencia para la comparacion)
ROWS = [
    ("constr_k2", r"Construction, $\kappa=2$", None),
    ("constr_k1", r"$\ast$ Construction, $\kappa=1$", "constr_k2"),
    ("swo", r"+ squeaky wheel loop ($T=20$)", "constr_k2"),
    ("swo_rho0", r"$\ast$ squeaky wheel without learning ($\rho=0$)", "swo"),
    ("swo_T26", r"$\ast$ squeaky wheel loop, $T=26$ (matched time)", "swo"),
    ("recomb", r"+ recombination ($T_{\mathrm{milp}}=60$)", "swo_T26"),
    ("harvest", r"+ harvest ($K=10$, \cfgbal{})", "recomb"),
]


def wilcoxon(d):
    """prueba de Wilcoxon bilateral (aproximacion normal con correccion por empates y por continuidad)"""
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return 1.0
    a = sorted((abs(x), x) for x in d)
    ranks = [0.0] * n
    i = 0
    ties = 0.0
    while i < n:
        j = i
        while j + 1 < n and a[j + 1][0] == a[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[k] = r
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    wplus = sum(r for r, (_, x) in zip(ranks, a) if x > 0)
    mu = n * (n + 1) / 4
    var = n * (n + 1) * (2 * n + 1) / 24 - ties / 48
    if var <= 0:
        return 1.0
    z = (abs(wplus - mu) - 0.5) / math.sqrt(var)
    return math.erfc(max(z, 0) / math.sqrt(2))


def fmt_p(p):
    if p < 1e-4:
        e = math.floor(math.log10(p))
        return rf"${p / 10 ** e:.0f}\cdot 10^{{{e}}}$"
    return f"{p:.2g}" if p < 0.01 else f"{p:.2f}"


def main():
    d = sys.argv[1]
    partial = "--partial" in sys.argv
    runs = list(csv.DictReader(open(f"{d}/runs.csv")))
    bad = [r for r in runs if r["bins"] == "" or r["valid"] != r["bins"]]
    if bad:
        sys.exit(f"{len(bad)} runs are incomplete or invalid, e.g. {bad[0]['config']} {bad[0]['seed']} {bad[0]['instance']}")
    res = defaultdict(dict)   # (config, seed) -> instance -> (bins, time)
    for r in runs:
        res[(r["config"], int(r["seed"]))][r["instance"]] = (int(r["bins"]), float(r["time"]))
    seeds = sorted({s for _, s in res})
    insts = set.intersection(*[set(v) for v in res.values()])
    full = {len(v) for v in res.values()}
    if not partial and (len(full) != 1 or len(insts) != 240):
        sys.exit(f"incomplete campaign ({len(insts)} common instances); use --partial for a provisional table")
    insts = sorted(insts)
    mean = {}
    for cfg, _, _ in ROWS:
        mean[cfg] = {i: sum(res[(cfg, s)][i][0] for s in seeds) / len(seeds) for i in insts}

    print(r"\begin{tabular}{@{}l" + "r" * len(seeds) + "rrrrl@{}}")
    print(r"\toprule")
    print("Configuration & " + " & ".join(f"Seed {s}" for s in seeds)
          + r" & Mean & Time (s) & Diff. & Better/worse & $p$\\")
    print(r"\midrule")
    for cfg, label, ref in ROWS:
        tot = [sum(res[(cfg, s)][i][0] for i in insts) for s in seeds]
        t = sum(res[(cfg, s)][i][1] for s in seeds for i in insts) / (len(seeds) * len(insts))
        m = sum(tot) / len(tot)
        if ref:
            diff = [mean[cfg][i] - mean[ref][i] for i in insts]
            better = sum(x < 0 for x in diff)
            worse = sum(x > 0 for x in diff)
            extra = f"{m - sum(mean[ref].values()):+.1f} & {better}/{worse} & {fmt_p(wilcoxon(diff))}"
        else:
            extra = "--- & --- & ---"
        print(f"{label} & " + " & ".join(str(x) for x in tot) + f" & {m:.1f} & {t:.1f} & {extra}\\\\")
    print(r"\bottomrule")
    print(r"\end{tabular}")
    print(f"% {len(insts)} instances, seeds {seeds}; reference of each row: "
          + ", ".join(f"{c} vs {r}" for c, _, r in ROWS if r))


if __name__ == "__main__":
    main()
