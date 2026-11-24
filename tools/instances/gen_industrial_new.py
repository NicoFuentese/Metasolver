r"""Dos conjuntos industriales NUEVOS (semilla fija 20261031), distintos de los usados para ajustar kappa y -t. Pallet 1200 x 800 x 2055 mm.

  nb_c<clase>_<n>_<i>   bootstrap por clase de las cajas de Instance_CG (misma distribucion, instancias nuevas, NO independientes del material
                        original): clases 1-4 x n en {500,1000,1500,2000} x 3.
  nc_c1_<n>_<i>         catalogo real products.csv (distribucion distinta): n en {500,1000,1500} x 8; cajas de producto con cantidades 1-12.

Entradas: carpeta con las Instance_CG ya convertidas (convert_instance_cg.py) y products.csv (columnas id,width,depth,height,weight,volume).
uso: python gen_industrial_new.py <carpeta cg convertida> <products.csv> <carpeta de salida>"""
import csv
import os
import random
import sys


def main(cg_dir, products, out):
    os.makedirs(out, exist_ok=True)
    rnd = random.Random(20261031)
    L, W, H = 1200, 800, 2055
    for c in (1, 2, 3, 4):
        pool = []
        for n in (500, 1000, 1500, 2000):
            for i in range(1, 6):
                ls = open(os.path.join(cg_dir, "cg_c%d_%d_%d.txt" % (c, n, i))).read().split("\n")
                pool += [tuple(map(int, l.split()[:3])) for l in ls[1:1 + n]]
        for n in (500, 1000, 1500, 2000):
            for i in range(1, 4):
                with open(os.path.join(out, "nb_c%d_%d_%d.txt" % (c, n, i)), "w") as f:
                    f.write("%d %d %d %d\n" % (n, L, W, H))
                    for _ in range(n):
                        f.write("%d %d %d\n" % rnd.choice(pool))
    prods = []
    for r in csv.reader(open(products)):
        if r[0] == "":
            continue
        try:
            l, w, h = int(r[2]), int(r[3]), int(r[4])
        except ValueError:
            continue  # encabezado
        if l <= L and w <= W and h <= H:
            prods.append((l, w, h))
    print(len(prods), "productos validos")
    for n in (500, 1000, 1500):
        for i in range(1, 9):
            boxes = []
            while len(boxes) < n:
                p = rnd.choice(prods)
                boxes += [p] * rnd.randint(1, 12)
            boxes = boxes[:n]
            rnd.shuffle(boxes)
            with open(os.path.join(out, "nc_c1_%d_%d.txt" % (n, i)), "w") as f:
                f.write("%d %d %d %d\n" % (n, L, W, H))
                for b in boxes:
                    f.write("%d %d %d\n" % b)
    print("ok", len(os.listdir(out)), "instancias en", out)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
