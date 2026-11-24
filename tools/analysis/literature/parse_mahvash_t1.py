r"""Parsea la Tabla 1 de Mahvash et al. (3D-BPP CON rotacion; 8 clases x n=50,100,150,200) desde el texto extraido con pdftotext -layout.
salida: mahvash_table1.csv  (class,n,LB,MP,CG,HGAs,BRKGA,CPU) y un resumen de totales para comprobar contra los totales impresos
(todas las clases: LB 8693, MP 8743, CG 9013, HGAs 9287, BRKGA 9009)."""
import csv, os, re
import sys
if len(sys.argv) < 2: sys.exit("uso: python parse_mahvash_t1.py <texto extraido con pdftotext -layout> [carpeta de salida (por defecto esta)]")
TXT = sys.argv[1]; SP = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
lines = open(TXT, encoding="utf-8", errors="replace").read().split("\n")
start = next(i for i, l in enumerate(lines) if "Table 1 CG, HGAs and BRKGA results" in l)
end = next(i for i, l in enumerate(lines) if i > start and "Total bin" in l)
rows = []
for l in lines[start:end]:
    nums = re.findall(r"\d+(?:\.\d+)?", l)
    if len(nums) >= 7:
        n, lb, mp, cg, hga, brkga, cpu = [float(x) for x in nums[-7:]]
        if int(n) in (50, 100, 150, 200): rows.append((int(n), lb, mp, cg, hga, brkga, cpu))
assert len(rows) == 32, len(rows)
out = []
for k, r in enumerate(rows): out.append((k // 4 + 1,) + r)
with open(os.path.join(SP, "mahvash_table1.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["class", "n", "LB", "MP", "CG", "HGAs", "BRKGA", "CPU"]); w.writerows(out)
tot = lambda idx, cls=None: sum(r[idx] for r in out if cls is None or r[0] in cls) * 10
print("todas las clases (x10): LB %.0f  MP %.0f  CG %.0f  HGAs %.0f  BRKGA %.0f" % tuple(tot(i) for i in (2, 3, 4, 5, 6)))
C = (1, 4, 5, 6, 7, 8)
print("clases 1,4-8 (x10):    LB %.0f  MP %.0f  CG %.0f  HGAs %.0f  BRKGA %.0f" % tuple(tot(i, C) for i in (2, 3, 4, 5, 6)))
print("HGAs < LB en:", [(r[0], r[1], r[5], r[2]) for r in out if r[5] < r[2] - 1e-9])
print("BRKGA < LB en:", [(r[0], r[1], r[6], r[2]) for r in out if r[6] < r[2] - 1e-9])


