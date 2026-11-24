r"""Corre una campana de BSG_BPP: varias configuraciones por instancia, en paralelo por instancias, validando cada solucion con el validador
independiente y escribiendo un CSV (una fila por instancia, escrita apenas termina).

Conjuntos de instancias (--set):
  original    MPV originales de problems/clp/benchs/MPV/original (clase c, n, instancia i); filas con columnas instance,class,n,lb,...
  flat        carpeta con archivos de una sola instancia (--dir); la instancia es el nombre del archivo; filas con columnas instance,lb,...
  industrial  Instance_CG convertidas (cg_c<clase>_<n>_<k>.txt, ver tools/instances/convert_instance_cg.py); se valida el apoyo (--support 0.7)

Cada configuracion es "etiqueta|argumentos del solver". Columnas por configuracion: <etiqueta>_bins, _swo, _time, _valid, _milp.
Una fila con "ERROR" indica que el solver no produjo resultado para alguna configuracion; el mensaje queda en <nombre>.errors.log.

uso: python run_campaign.py <nombre> --seed 1 [--procs 4] [--set original|flat|industrial] [--classes 1,4,5,6,7,8] [--insts 1,2,...]
         [--ns 50,100,150,200] [--dir CARPETA] [--only c1_150_5,c8_100_4] [--exe RUTA] [--keep-sol] "Fast|-T 4 -t 0.005 --harvest 10 --milp 30" ...
Salida en $BPP_OUT (por defecto results/bpp/campaigns). Ver tools/README.md."""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("name")
ap.add_argument("cfgs", nargs="+", help='"etiqueta|argumentos"')
ap.add_argument("--seed", default="1")
ap.add_argument("--procs", type=int, default=4)
ap.add_argument("--set", dest="kind", default="original", choices=["original", "flat", "industrial"])
ap.add_argument("--classes", default=None)
ap.add_argument("--insts", default=None)
ap.add_argument("--ns", default=None)
ap.add_argument("--dir", default=None)
ap.add_argument("--only", default=None, help="solo estas instancias (ids como c1_150_5, o nombre de archivo en --set flat)")
ap.add_argument("--exe", default=None)
ap.add_argument("--keep-sol", action="store_true", help="conservar las soluciones (por defecto se borran tras validar)")
a = ap.parse_args()

config.lower_priority()
EXE = a.exe or config.exe()
ENV = config.process_env()
OUT = config.out_dir()
cfgs = [c.split("|", 1) for c in a.cfgs]
sol_dir = os.path.join(OUT, a.name + "_sol")
os.makedirs(sol_dir, exist_ok=True)
errlog = os.path.join(OUT, a.name + ".errors.log")
ints = lambda s: [int(x) for x in s.split(",")]
only = set(a.only.split(",")) if a.only else None

# --- trabajos: (id, archivo, args del solver para elegir la instancia, args del validador, columnas extra) ---
jobs = []
if a.kind == "original":
    classes = ints(a.classes or "1,4,5,6,7,8"); insts = ints(a.insts or "1,2,3,4,5,6,7,8,9,10"); ns = ints(a.ns or "50,100,150,200")
    for c in classes:
        for n in ns:
            for i in insts:
                jid = "c%d_%d_%d" % (c, n, i)
                if only and jid not in only: continue
                jobs.append((jid, os.path.join(config.MPV_ORIGINAL, "class%d" % c, "%d.txt" % n), ["-i", str(i)], ["-i", str(i)], [c, n]))
elif a.kind == "industrial":
    if not a.dir: sys.exit("--set industrial necesita --dir (carpeta con los cg_c*_n_k.txt)")
    classes = ints(a.classes or "1,2,3,4"); insts = ints(a.insts or "1,2,3,4,5"); ns = ints(a.ns or "500,1000,1500,2000")
    for c in classes:
        for n in ns:
            for k in insts:
                jid = "c%d_%d_%d" % (c, n, k)
                if only and jid not in only: continue
                jobs.append((jid, os.path.join(a.dir, "cg_c%d_%d_%d.txt" % (c, n, k)), [], [], [c, n]))
    jobs.sort(key=lambda j: -j[4][1])  # las grandes primero: mejor reparto entre procesos
else:
    if not a.dir: sys.exit("--set flat necesita --dir")
    for fn in sorted(os.listdir(a.dir)):
        if not fn.endswith(".txt"): continue
        jid = fn[:-4]
        if only and jid not in only and fn not in only: continue
        jobs.append((jid, os.path.join(a.dir, fn), ["-i", "1"], ["-i", "1"], []))
if not jobs: sys.exit("ninguna instancia seleccionada")
with_cn = a.kind != "flat"


def run(jid, f, sargs, vargs, tag, args):
    sol = os.path.join(sol_dir, "%s_%s.csv" % (jid, tag))
    p = subprocess.run([EXE, f] + sargs + ["-o", sol, "--seed", str(a.seed)] + args.split(), capture_output=True, text=True, env=ENV)
    m = re.search(r"n_bins (\d+) lb (\d+) construction (\d+) swo (\d+) t_construction \S+ time (\S+)", p.stdout)
    if not m:
        with open(errlog, "a") as fh:
            fh.write("%s %s: %s %s\n" % (jid, tag, p.stdout[-300:].strip(), p.stderr[-300:].strip()))
        return None
    extra = list(vargs) + (["--rot"] if "--rot" in args.split() else [])
    if a.kind == "industrial": extra += ["--support", "0.7"]
    elif "--support" in args.split(): extra += ["--support", "0.7"]
    v = config.validate(f, sol, extra)
    ml = " ".join(l for l in p.stdout.split("\n") if l.startswith("milp"))
    if not a.keep_sol:
        try: os.remove(sol)
        except OSError: pass
    return dict(bins=int(m.group(1)), lb=int(m.group(2)), swo=int(m.group(4)), time=float(m.group(5)), valid=(v == m.group(1)), milp=ml)


def job(j):
    jid, f, sargs, vargs, cn = j
    return j, [run(jid, f, sargs, vargs, t, ar) for t, ar in cfgs]


t0 = time.time()
hdr = ["instance"] + (["class", "n"] if with_cn else []) + ["lb"]
for t, _ in cfgs: hdr += [t + "_bins", t + "_swo", t + "_time", t + "_valid", t + "_milp"]
with open(os.path.join(OUT, a.name + ".csv"), "w", newline="") as fh, ThreadPoolExecutor(a.procs) as ex:
    w = csv.writer(fh); w.writerow(hdr)
    for j, rs in ex.map(job, jobs):
        head = [j[0]] + (j[4] if with_cn else [])
        if any(r is None for r in rs): w.writerow(head + ["", "ERROR"])
        else:
            w.writerow(head + [rs[0]["lb"]] + [x for r in rs for x in (r["bins"], r["swo"], "%.2f" % r["time"], r["valid"], r["milp"])])
        fh.flush()
if not a.keep_sol:
    shutil.rmtree(sol_dir, ignore_errors=True)
print(a.name, "terminada en %.0f s" % (time.time() - t0))
