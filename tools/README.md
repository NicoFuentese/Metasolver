# tools/ — herramientas de experimentación de BSG_BPP

Todo lo necesario para regenerar las instancias, correr las campañas del paper y reconstruir sus tablas. Nada depende de una máquina concreta:
las rutas se deducen de la ubicación del repo y se cambian con variables de entorno (ver `config.py`).

```
tools/
  config.py                    rutas, entorno del solver y validación (compartido por todo)
  instances/                   generadores y conversores de instancias
    gen_mpv_sets.py            conjuntos MPV nuevos con semillas registradas: blind2 (128) y large (36)
    convert_instance_cg.py     Instance_CG (Elhedhli, Gzara y Yildiz) -> formato BSG_BPP, pallet 1200x800x2055 mm
  runners/
    run_campaign.py            corre varias configuraciones por instancia en paralelo, valida cada solución y escribe un CSV
  chains/
    paper_campaigns.ps1        todas las campañas del paper (configuraciones exactas, 3 semillas); -List las muestra
  analysis/
    common.py                  carga de CSV, totales, comparaciones apareadas (Wilcoxon), estadísticas del MILP
    an_*.py                    tablas del paper (ver abajo)
    literature/                cifras de la literatura (CSV) y los parsers que las extraen de los PDF
```

## Requisitos
- `BSG_BPP` compilado con HiGHS (opción `--milp`); Python 3 con `numpy` y `scipy` para el análisis.
- En Windows, la carpeta `bin` de MSYS2/UCRT64 con las DLL de g++ (`BPP_MSYS`, por defecto `C:\msys64\ucrt64\bin`); sin ella el `.exe` termina en silencio.
- Los datos de Instance_CG y `products.csv` no están en el repo (vienen de la carpeta de Drive del benchmark): `BPP_DATA` apunta a ellos.

## Flujo
```powershell
# 1. Instancias (fuera del repo si se quiere: BPP_OUT / --Instances)
python tools/instances/gen_mpv_sets.py blind2 results/bpp/campaigns/instances/blind2
python tools/instances/gen_mpv_sets.py large  results/bpp/campaigns/instances/large_mpv
python tools/instances/convert_instance_cg.py results/bpp/campaigns/instances/cg  $env:BPP_DATA/Instance_CG

# 2. Campañas (una a la vez; 4 procesos; los CSV quedan en $BPP_OUT)
powershell -File tools/chains/paper_campaigns.ps1 -Only orig,quality,ctl -Exe build/BSG_BPP.exe

# 3. Tablas (leen los CSV de $BPP_RESULTS, por defecto $BPP_OUT)
python tools/analysis/an_mpv.py
```
Una sola campaña o instancia suelta: `python tools/runners/run_campaign.py prueba --seed 1 --classes 1 --ns 50 --insts 1 "Fast|-T 4 -t 0.005 --harvest 10 --milp 30"`
(`--only c1_150_5` reejecuta solo esa instancia, útil para filas ERROR). Cada solución se valida con `problems/clp/validate_bpp.py` (con `--rot` y/o `--support`
según la configuración); una fila con `valid=False` o `ERROR` nunca debe entrar en una tabla sin explicarlo.

## Qué script produce qué
| Script | Campañas (CSV) | Contenido |
|---|---|---|
| `an_mpv.py` | `orig`, `quality`, `ctl`, `equiv_new`, `cls23_fixed` | MPV sin rotación: totales por configuración, controles de squeaky wheel a igual tiempo, equivalencia entre versiones del código, clases 2,3, estadísticas del MILP |
| `an_abl_sens.py` | `abl`, `sens`, `ctl` | ablación de la réplica y sensibilidad de ρ, σ, fracción de bins, K, θ y t |
| `an_cloud.py` | `abl` + `results/bpp/ablation_2026-11/runs.csv` | comparación de la réplica con la ablación principal (la de la nube) |
| `an_rot.py` | `rot_orig`, `rot_cls23` | rotación frente a Mahvash CG y BRKGA, por celda y por tamaño |
| `an_blind.py` | `blind2rep` | segundo conjunto ciego: harvest, MILP con objetivo frente al simple, cota LP |
| `an_ind.py` | `ind_large`, `ind_small` | industrial con apoyo ≥ 70 % frente a LCGA |
| `an_ind_extra.py` | `ind_kappa`, `ind_support` | tiempo por contenedor y κ al mismo tiempo; costo de los criterios de apoyo (con `support_stats.py`) |
| `an_extra.py` | `rotctl`, `rotctl23`, `qharv`, `large` | controles de squeaky wheel con rotación a igual tiempo y F4 con rotación, Quality con harvest, escala n=500/1000 (usa las semillas e instancias disponibles, sirve con campañas a medias) |
| `an_cells.py` | `orig`, `quality`, `cls23_fixed` | celdas frente a BRKGA (comparación estricta con `TOL=0.0001`; el paper usa la estricta) |

La ablación principal del paper es la de `results/bpp/ablation_2026-11/` (`problems/clp/experiments/run_ablation.sh` y `table_ablation.py`).

## Condiciones y advertencias
- Compare solo campañas corridas en las mismas condiciones (misma máquina, mismo número de procesos, misma prioridad, un binario). Las diferencias de unos
  pocos bins entre campañas distintas son ruido de reloj de pared (los límites `-T`, `--milp` son de tiempo real).
- Los binarios anteriores al arreglo del greedy pueden terminar con `a box does not fit in the bin` con `-t 0.005`; `run_campaign.py` anota esas filas
  como `ERROR` y deja el mensaje en `<nombre>.errors.log`.
- `paper_campaigns.ps1`: la campaña `sens` necesita un ejecutable con `--swo_sigma` y `--swo_bins`, que no están en el repo (`-SensExe`).
