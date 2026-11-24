"""Rutas y utilidades comunes de las herramientas de experimentacion de BSG_BPP.

Nada de aqui depende de una maquina concreta: todo se deduce de la ubicacion del repo y se puede cambiar con variables de entorno.

  BPP_EXE       ejecutable de BSG_BPP (por defecto build/BSG_BPP[.exe] del repo)
  BPP_OUT       carpeta de resultados (CSV y soluciones; por defecto results/bpp/campaigns)
  BPP_RESULTS   carpetas donde buscar CSV de campanas para el analisis, separadas por el separador de rutas del sistema (por defecto BPP_OUT)
  BPP_DATA      carpeta con los datos descargados (Instance_CG/, products.csv); solo la usan las herramientas de instancias
  BPP_MSYS      carpeta bin de MSYS2/UCRT64 con las DLL de g++ (solo Windows; por defecto C:\\msys64\\ucrt64\\bin si existe)
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(TOOLS)
VALIDATOR = os.path.join(REPO, "problems", "clp", "validate_bpp.py")
MPV_ORIGINAL = os.path.join(REPO, "problems", "clp", "benchs", "MPV", "original")
GEN_MPV = os.path.join(REPO, "problems", "clp", "benchs", "MPV", "gen_mpv.py")
LITERATURE = os.path.join(TOOLS, "analysis", "literature")


def exe():
    name = "BSG_BPP.exe" if os.name == "nt" else "BSG_BPP"
    return os.environ.get("BPP_EXE", os.path.join(REPO, "build", name))


def out_dir():
    d = os.environ.get("BPP_OUT", os.path.join(REPO, "results", "bpp", "campaigns"))
    os.makedirs(d, exist_ok=True)
    return d


def result_dirs():
    v = os.environ.get("BPP_RESULTS")
    return [p for p in v.split(os.pathsep) if p] if v else [out_dir()]


def process_env():
    """Entorno para lanzar el solver: en Windows antepone la carpeta de las DLL de MSYS2 (sin ella el .exe termina en silencio)."""
    env = dict(os.environ)
    if os.name == "nt":
        msys = os.environ.get("BPP_MSYS", r"C:\msys64\ucrt64\bin")
        if os.path.isdir(msys):
            env["PATH"] = msys + os.pathsep + env["PATH"]
    return env


def lower_priority():
    """Prioridad inferior a la normal para no sesgar los tiempos de otras campanas ni bloquear la maquina."""
    try:
        if os.name == "nt":
            import ctypes
            k = ctypes.WinDLL("kernel32")
            k.GetCurrentProcess.restype = ctypes.c_void_p
            k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
            k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)  # BELOW_NORMAL_PRIORITY_CLASS
        else:
            os.nice(5)
    except Exception:
        pass


def validate(instance_file, solution_file, extra=()):
    """Valida una solucion con el validador independiente (problems/clp/validate_bpp.py). Devuelve el ultimo renglon (nº de bins) o ''."""
    cmd = [sys.executable, "-I", VALIDATOR, instance_file, solution_file] + list(extra)
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split("\n")
    return out[-1] if out else ""
