r"""Parsea la Tabla 2 de Mahvash et al. (3D-BPP SIN rotacion; 8 clases x n=50,100,150,200) desde el texto extraido con pdftotext -layout.
salida: mahvash_table2.csv  (class,n,LB1,LB2,MP,CG,HGAs,BRKGA) con promedios de 10 instancias, y un resumen de totales para comprobar contra los
impresos (clases 1,4-8: CG 7252, BRKGA 7258; todas las clases: CG 9766, HGAs 9769, BRKGA 9777)."""
import csv, os, re
import sys
if len(sys.argv) < 2: sys.exit("uso: python parse_mahvash_t2.py <texto extraido con pdftotext -layout> [carpeta de salida (por defecto esta)]")
TXT = sys.argv[1]; SP = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
lines = open(TXT, encoding="utf-8", errors="replace").read().split("\n")
start = next(i for i, l in enumerate(lines) if "Table 2 Results for the 3D-BPP with no rotation" in l)
end = next(i for i, l in enumerate(lines) if i > start and l.strip().startswith("1,4-8"))
rows, cls = [], 0
for l in lines[start:end]:
    tok = re.findall(r"\d+(?:\.\d+)?", l)
    if not tok: continue
    # primera fila de una clase: clase, tamano del bin, n, ...; el resto: n, ...
    if len(tok) >= 3 and tok[0] in "12345678" and len(tok[0]) == 1 and tok[2] in ("50", "100", "150", "200") and tok[1] in ("100", "10", "40"):
        cls = int(tok[0]); tok = tok[2:]
    if tok[0] in ("50", "100", "150", "200") and len(tok) >= 8:
        rows.append((cls, int(tok[0])) + tuple(float(x) for x in tok[1:7]))
assert len(rows) == 32, len(rows)
with open(os.path.join(SP, "mahvash_table2.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["class", "n", "LB1", "LB2", "MP", "CG", "HGAs", "BRKGA"]); w.writerows(rows)
tot = lambda idx, cl: sum(r[idx] for r in rows if r[0] in cl) * 10
for name, cl in (("clases 1,4-8", (1, 4, 5, 6, 7, 8)), ("todas", tuple(range(1, 9)))):
    print("%s (x10): CG %.0f  HGAs %.0f  BRKGA %.0f" % (name, tot(5, cl), tot(6, cl), tot(7, cl)))
