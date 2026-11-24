r"""Conjuntos de instancias MPV nuevos, con la distribucion de problems/clp/benchs/MPV/gen_mpv.py y semillas registradas (reproducibles).

  blind2   128 instancias: 8 clases x n en {50,100,150,200} x 4. Semilla de cada instancia: 9000000 + 1000000*clase + 1000*n + i.
           Nunca usadas en ningun ajuste (segundo conjunto ciego del paper).
  large    36 instancias: clases 1,4-8 x n en {500,1000} x 3. Semilla: 9500000 + 1000000*clase + 1000*n + i. Para la prueba de escala.

Cada instancia queda en <salida>/c<clase>_<n>_<i>.txt (formato "n L W H" y una linea "l w h" por caja).
uso: python gen_mpv_sets.py {blind2|large} <carpeta de salida>"""
import importlib.util
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config  # noqa: E402

SETS = {
    "blind2": dict(base=9000000, classes=range(1, 9), ns=(50, 100, 150, 200), insts=range(1, 5)),
    "large": dict(base=9500000, classes=(1, 4, 5, 6, 7, 8), ns=(500, 1000), insts=range(1, 4)),
}


def main(kind, out):
    s = SETS[kind]
    spec = importlib.util.spec_from_file_location("gen_mpv", config.GEN_MPV)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    os.makedirs(out, exist_ok=True)
    for cls in s["classes"]:
        for n in s["ns"]:
            for i in s["insts"]:
                rng = random.Random(s["base"] + 1000000 * cls + 1000 * n + i)
                boxes = [g.box(rng, cls) for _ in range(n)]
                B = boxes[0][0]
                with open(os.path.join(out, "c%d_%d_%d.txt" % (cls, n, i)), "w") as f:
                    f.write("%d %d %d %d\n" % (n, B, B, B))
                    for _, d in boxes:
                        f.write(" ".join(map(str, d)) + "\n")
    print("ok", len(os.listdir(out)), "instancias en", out)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in SETS:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
