#!/usr/bin/env python3
"""Target runner de irace para BSG_BPP.

irace lo llama como: target-runner.py <configID> <instanceID> <seed> <instance> <bound> <parametros...>
Corre BSG_BPP con el presupuesto fijo de Fast (-T 4 -t 0.005 --milp 30; los limites de tiempo y tau no se ajustan,
son decisiones de diseno), valida la solucion con el validador independiente y escribe el costo (numero de
contenedores) en la salida estandar. Una solucion invalida o un error terminan con codigo distinto de cero para que
irace lo informe. BPP_EXE elige el ejecutable (por defecto build/BSG_BPP del repositorio)."""
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
EXE = os.environ.get("BPP_EXE", os.path.join(REPO, "build", "BSG_BPP.exe" if os.name == "nt" else "BSG_BPP"))
FIXED = ["-T", "4", "-t", "0.005", "--milp", "30"]


def main():
    _cfg, _iid, seed, instance, _bound = sys.argv[1:6]
    params = sys.argv[6:]
    inst = instance if os.path.isabs(instance) else os.path.join(REPO, instance)
    with tempfile.TemporaryDirectory() as tmp:
        sol = os.path.join(tmp, "sol.csv")
        r = subprocess.run([EXE, inst, "--seed", seed, "-o", sol] + FIXED + params, capture_output=True, text=True)
        m = re.search(r"^n_bins (\d+)", r.stdout, re.M)
        if r.returncode != 0 or not m:
            sys.exit(f"BSG_BPP failed: {r.stderr.strip()[-300:]}")
        v = subprocess.run([sys.executable, "-I", os.path.join(REPO, "problems", "clp", "validate_bpp.py"), inst, sol],
                           capture_output=True, text=True)
        if v.returncode != 0 or v.stdout.strip() != m.group(1):
            sys.exit(f"invalid solution: {v.stderr.strip()[-300:]}")
    print(m.group(1))


if __name__ == "__main__":
    main()
