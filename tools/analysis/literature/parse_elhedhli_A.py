r"""Parsea las Tablas A.1-A.4 (resultados de LCGA instancia por instancia, 160 filas) de Elhedhli, Gzara y Yildiz (2019) desde el texto de pdftotext -layout.
salida: elhedhli_A.csv (class,n,inst,cpu,lb_L2,bins,support_avg,items_supported_pct) y resumenes."""
import csv, os, re, collections, statistics as st
import sys
if len(sys.argv) < 2: sys.exit("uso: python parse_elhedhli_A.py <texto extraido con pdftotext -layout> [carpeta de salida (por defecto esta)]")
TXT = sys.argv[1]; SP = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
lines = open(TXT, encoding="utf-8", errors="replace").read().split("\n")
start = next(i for i, l in enumerate(lines) if "Table A.1. Generated Instances: Class 1" in l)
cls = 0; rows = []
row_re = re.compile(r"^\s*([\d,]+)\s+(\d)\s+([\d,]+\.\d+)\s+(\d+(?:\.\d+)?)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$")
for l in lines[start:]:
    m = re.search(r"Table A\.(\d)\. Generated Instances: Class (\d)", l)
    if m: cls = int(m.group(2)); continue
    m = row_re.match(l)
    if m and cls:
        n = int(m.group(1).replace(",", "")); rows.append((cls, n, int(m.group(2)), float(m.group(3).replace(",", "")), float(m.group(4)), int(m.group(5)), float(m.group(6)), float(m.group(7))))
print("filas parseadas:", len(rows), "(esperado 160)")
with open(os.path.join(SP, "elhedhli_A.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["class", "n", "inst", "cpu", "lb_L2", "bins", "support_avg", "items_supported_pct"]); w.writerows(rows)
cells = collections.defaultdict(list)
for r in rows: cells[(r[0], r[1])].append(r)
print("celdas:", len(cells), "| filas por celda:", sorted(set(len(v) for v in cells.values())))
print("clase n | bins promedio (Tabla 9) | cpu medio | items con >=70%% de soporte (media, min, max) | soporte medio")
tot_bins = tot_cpu = 0
for key in sorted(cells):
    v = cells[key]
    print("  %d %5d | %6.2f | %7.1f s | %5.1f %% (%5.1f-%5.1f) | %5.1f" % (key[0], key[1], st.mean(r[5] for r in v), st.mean(r[3] for r in v), st.mean(r[7] for r in v), min(r[7] for r in v), max(r[7] for r in v), st.mean(r[6] for r in v)))
    tot_bins += st.mean(r[5] for r in v)
print("suma de promedios de bins en las 32 celdas: %.1f (Tabla 9 promedio global 5.52 x 32 = %.1f)" % (tot_bins, 5.52 * 32))
big = [r for r in rows if r[1] >= 500]; small = [r for r in rows if r[1] < 500]
print("n>=500 (80 inst.): items con >=70%% de soporte: media %.1f %% | min %.1f | max %.1f | soporte medio %.1f %%" % (st.mean(r[7] for r in big), min(r[7] for r in big), max(r[7] for r in big), st.mean(r[6] for r in big)))
print("n<500  (80 inst.): items con >=70%% de soporte: media %.1f %% | min %.1f | max %.1f | soporte medio %.1f %%" % (st.mean(r[7] for r in small), min(r[7] for r in small), max(r[7] for r in small), st.mean(r[6] for r in small)))
print("todas: items con >=70%% de soporte: media %.1f %%; instancias con 100%%: %d" % (st.mean(r[7] for r in rows), sum(1 for r in rows if r[7] >= 99.999)))


