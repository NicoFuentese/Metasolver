"""Funciones comunes del analisis de campanas (carga de CSV, totales, comparaciones apareadas con Wilcoxon).
Los CSV se buscan en $BPP_RESULTS (carpetas separadas por el separador de rutas; por defecto $BPP_OUT)."""
import csv, os, re, warnings
import numpy as np
from scipy.stats import wilcoxon
warnings.filterwarnings("ignore")
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import config  # noqa: E402
LIT = config.LITERATURE
REPO = config.REPO
R22 = R11 = IND = None  # compatibilidad: los CSV se buscan en las carpetas de $BPP_RESULTS (ver find)


def find(fname):
    """Busca un CSV de campana en las carpetas de $BPP_RESULTS (por defecto $BPP_OUT)."""
    for d in config.result_dirs():
        p = os.path.join(d, fname)
        if os.path.exists(p):
            return p
    return os.path.join(config.result_dirs()[0], fname)


def load(path):
    """-> (dict inst -> dict cfg -> rec, lista de instancias con ERROR)."""
    rows, errs = {}, []
    if not os.path.exists(path):
        return rows, errs
    with open(path, newline="") as fh:
        rd = csv.DictReader(fh)
        cfgs = [c[:-5] for c in rd.fieldnames if c.endswith("_bins")]
        for r in rd:
            if r.get("lb", "") == "" or any(v == "ERROR" for v in r.values()):
                errs.append(r["instance"]); continue
            d = {"lb": int(r["lb"])}
            for c in cfgs:
                m = r.get(c + "_milp", "") or ""
                d[c] = dict(bins=int(r[c + "_bins"]), swo=int(r[c + "_swo"]), time=float(r[c + "_time"]),
                            valid=(r[c + "_valid"] == "True"), milp=m)
            rows[r["instance"]] = d
    return rows, errs


def camp(folder, name, seeds=(1, 2, 3)):
    out = []
    for s in seeds:
        d, e = load(find("%s_s%d.csv" % (name, s)))
        out.append((d, e))
    return out


def common(camps, cfgs_list):
    """instancias presentes en todas las semillas de todas las campanas (para los cfgs dados)."""
    s = None
    for cp, cfgs in zip(camps, cfgs_list):
        for d, _ in cp:
            for c in cfgs:
                k = {i for i, v in d.items() if c in v}
                s = k if s is None else s & k
    return sorted(s) if s else []


def tots(cp, cfg, insts, key="bins"):
    return [sum(d[i][cfg][key] for i in insts) for d, _ in cp]


def sd(x):
    return float(np.std(x, ddof=1)) if len(x) > 1 else float("nan")


def tmean(cp, cfg, insts):
    v = [d[i][cfg]["time"] for d, _ in cp for i in insts]
    return float(np.mean(v)), float(np.median(v)), float(np.percentile(v, 90)), float(np.max(v))


def invalid(cp, cfg, insts):
    return sum(1 for d, _ in cp for i in insts if not d[i][cfg]["valid"])


def wp(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    dd = a - b
    if np.all(dd == 0):
        return 1.0
    try:
        return float(wilcoxon(a, b, zero_method="wilcox", correction=False).pvalue)
    except Exception:
        return float("nan")


def cmp(cpA, cfgA, cpB, cfgB, insts, label=""):
    """A - B (A es la config comparada, B la referencia). Por semilla y sobre medias por instancia."""
    ta, tb = tots(cpA, cfgA, insts), tots(cpB, cfgB, insts)
    diffs = [x - y for x, y in zip(ta, tb)]
    per = []
    for (da, _), (db, _) in zip(cpA, cpB):
        a = [da[i][cfgA]["bins"] for i in insts]; b = [db[i][cfgB]["bins"] for i in insts]
        per.append((sum(1 for x, y in zip(a, b) if x < y), sum(1 for x, y in zip(a, b) if x > y), wp(a, b)))
    ma = [np.mean([d[i][cfgA]["bins"] for d, _ in cpA]) for i in insts]
    mb = [np.mean([d[i][cfgB]["bins"] for d, _ in cpB]) for i in insts]
    pm = wp(ma, mb)
    bet = sum(1 for x, y in zip(ma, mb) if x < y); wor = sum(1 for x, y in zip(ma, mb) if x > y)
    print("  %-34s dif medio %+7.1f (por semilla %s)  mejor/peor sobre medias %d/%d  p(medias)=%.4g  p por semilla %s"
          % (label, np.mean(diffs), ",".join("%+d" % d for d in diffs), bet, wor, pm,
             "/".join("%.3g" % p[2] for p in per)))
    return np.mean(diffs), pm


def line(label, cp, cfg, insts, lit=None):
    t = tots(cp, cfg, insts)
    tm = tmean(cp, cfg, insts)
    s = "  %-26s %s  media %8.1f +- %.1f   t medio %.1f (med %.1f p90 %.1f max %.1f)  invalidas %d" % (
        label, "/".join(str(x) for x in t), np.mean(t), sd(t), tm[0], tm[1], tm[2], tm[3], invalid(cp, cfg, insts))
    print(s)


def milp_stats(cp, cfg, insts):
    n = imp = lp = pr = tl = 0
    tm = []
    for d, _ in cp:
        for i in insts:
            r = d[i][cfg]
            if "milp" not in r["milp"]:
                continue
            n += 1
            imp += r["swo"] > r["bins"]
            m = re.search(r"lp_proof (\d)", r["milp"]); lp += (m and m.group(1) == "1") or 0
            m = re.search(r"proven (\d)", r["milp"]); pr += (m and m.group(1) == "1") or 0
            m = re.search(r"t_milp (\S+)", r["milp"]);
            if m: tm.append(float(m.group(1)))
    return n, imp, lp, pr, (np.mean(tm) if tm else float("nan"))

