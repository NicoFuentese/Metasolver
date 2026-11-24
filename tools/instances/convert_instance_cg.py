r"""Convierte las instancias de Instance_CG (benchmark industrial de Elhedhli, Gzara y Yildiz) al formato de BSG_BPP: "n L W H" y una linea "l w h"
por caja (cada fila del original se repite tantas veces como indica su columna 9). Pallet de 1200 x 800 x 2055 mm: es el pallet del articulo, pero los
archivos originales NO traen sus dimensiones. Escribe cg_c<clase>_<n>_<k>.txt, donde k es el numero de instancia del nombre de archivo.

Entrada: carpeta Instance_CG con subcarpetas 50, 100, 150, 200, 500, 1000, 1500, 2000 (por defecto $BPP_DATA/Instance_CG).
uso: python convert_instance_cg.py <carpeta de salida> [carpeta Instance_CG]"""
import os
import re
import sys

PALLET = (1200, 800, 2055)


def main(dst, src):
    os.makedirs(dst, exist_ok=True)
    tot = 0
    for n in (50, 100, 150, 200, 500, 1000, 1500, 2000):
        for fn in sorted(os.listdir(os.path.join(src, str(n)))):
            m = re.match(r"bin_pack_instance_i\((\d+)\)_c\((\d+)\)_s\(", fn)
            if not m:
                continue
            k, c = int(m.group(1)), int(m.group(2))
            boxes = []
            for ln in open(os.path.join(src, str(n), fn)):
                f = ln.split()
                if len(f) < 9:
                    continue
                boxes += [(int(f[0]), int(f[1]), int(f[2]))] * int(f[8])
            assert len(boxes) == n, (fn, len(boxes))
            with open(os.path.join(dst, "cg_c%d_%d_%d.txt" % (c, n, k)), "w") as o:
                o.write("%d %d %d %d\n" % ((n,) + PALLET))
                for b in boxes:
                    o.write("%d %d %d\n" % b)
            tot += 1
    print(tot, "instancias convertidas en", dst)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get("BPP_DATA", ""), "Instance_CG")
    main(sys.argv[1], src)
