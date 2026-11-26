r"""Estadisticas de apoyo vertical de soluciones de BSG_BPP (pallet 1200 x 800 mm).

Para cada caja de cada contenedor calcula la fraccion de su base que descansa sobre las caras superiores de otras cajas del mismo contenedor
(1 si esta en el piso). Resume, por configuracion de una campana: apoyo medio, proporcion de cajas con apoyo >= 0.7 y proporcion con apoyo completo.

Lee las soluciones conservadas (run_campaign.py --keep-sol) en <BPP_OUT>/<campana>_sol/<instancia>_<etiqueta>.csv (formato bin;item;x;y;z;l;w;h).
uso: python support_stats.py <campana> <etiqueta> [<etiqueta> ...]"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402


def stats(path):
    bins = {}
    with open(path, newline="") as fh:
        for r in csv.reader(fh, delimiter=";"):
            try:
                b, _, x, y, z, l, w, h = (int(v) for v in r[:8])
            except ValueError:
                continue
            bins.setdefault(b, []).append((x, y, z, l, w, h))
    tot = n70 = full = 0
    ssum = 0.0
    for boxes in bins.values():
        for (x, y, z, l, w, h) in boxes:
            tot += 1
            if z == 0:
                s = 1.0
            else:
                cov = 0
                for (x2, y2, z2, l2, w2, h2) in boxes:
                    if z2 + h2 == z:
                        dx = min(x + l, x2 + l2) - max(x, x2)
                        dy = min(y + w, y2 + w2) - max(y, y2)
                        if dx > 0 and dy > 0:
                            cov += dx * dy
                s = cov / float(l * w)
            ssum += s
            n70 += s >= 0.7 - 1e-9
            full += s >= 1.0 - 1e-9
    return tot, ssum, n70, full


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    name, tags = sys.argv[1], sys.argv[2:]
    d = os.path.join(config.out_dir(), name + "_sol")
    for tag in tags:
        tot = ssum = n70 = full = 0
        files = glob.glob(os.path.join(d, "*_%s.csv" % tag))
        for f in files:
            t, s, a, b = stats(f)
            tot += t; ssum += s; n70 += a; full += b
        print("%-8s soluciones %3d  cajas %8d  apoyo medio %.1f%%  cajas con >=70%% %.1f%%  cajas con apoyo completo %.1f%%" % (
            tag, len(files), tot, 100 * ssum / tot, 100 * n70 / tot, 100 * full / tot))


if __name__ == "__main__":
    main()
