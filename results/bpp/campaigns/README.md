# Resultados de las campañas del paper (`escritos/bpp`)

Un CSV por campaña y semilla (`<campaña>_s<semilla>.csv`), con una fila por instancia y configuración, validada con `problems/clp/validate_bpp.py`.
Protocolo: 3 semillas, 4 procesos en paralelo, prioridad inferior a la normal, un Intel i5-14400, tiempos de pared. Las tablas se reconstruyen con
`tools/analysis` (`BPP_RESULTS=results/bpp/campaigns`). Las soluciones y los registros de ejecución no se incluyen.

## Ejecutable de cada campaña (SHA-256)

| Campañas | Ejecutable | Código | SHA-256 |
|---|---|---|---|
| `orig`, `quality`, `ctl`, `cls23_fixed`, `blind2rep`, `abl`, `qharv`, `rot_orig`, `rot_cls23`, `rotctl`, `rotctl23` | `BSG_BPP_d62ea4a18.exe` | commit `d62ea4a18` (anterior al arreglo del greedy con `-t 0.005`) | `3E70773C7F3070A3153C5CF1BBFF4D2954FB20E6145BF83C03C2E139BBA2ECBA` |
| `sens` | compilado de una copia de `d62ea4a18` con `--swo_sigma` y `--swo_bins` (valores por defecto idénticos; las opciones están hoy en el repositorio) | `d62ea4a18` + opciones | `FE857EAC164131FE30F8670BC756E824EFEBE50FB42B1A69AC671FE98FE564C2` |
| `equiv_new`, `large`, `ind_large`, `ind_small`, `ind_kappa`, `ind_support` | `BSG_BPP_5c011841b.exe` | commit `5c011841b` (con el arreglo del greedy y `--partition`) | `ED5CE9A66DF7D798BFAFE2A3DF912B7CA7671C351B74F01C2122BC6DC3E65E62` |

## Filas con error
- `abl_s2.csv`: la instancia `c1_150_5` terminó con `a box does not fit in the bin` (error del greedy corregido en `5c011841b`). Se reejecutó sola con el mismo ejecutable y semilla: `abl_s2_rerun_c1_150_5.csv`.
- `rotctl_s1.csv`: ídem con `c4_100_7`; reejecución en `rotctl_s1_rerun_c4_100_7.csv` y el original en `rotctl_s1_original_con_ERROR.csv`. Los análisis usan la reejecución.
- Con el binario `d62ea4a18` y `-t 0.005` el error aparece en alrededor de 1 de cada 1500 corridas.
