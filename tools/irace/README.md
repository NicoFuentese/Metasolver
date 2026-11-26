# Ajuste de BSG_BPP con irace

Escenario para ajustar, una sola vez y en el conjunto de desarrollo, los parametros que introduce el metodo:
`kappa`, `swo_rate` (rho), `swo_sigma` (sigma), `swo_bins` (fraccion de contenedores menos cargados), `harvest` (K) y
`harvest_thr` (theta). Los parametros de BSG quedan en los valores de Araya et al. (2017).

**Objetivo: simplificar.** Los rangos incluyen `swo_sigma=0` (sin ruido) y `harvest=0` (sin harvest). Si irace elige
valores cercanos a esos, el componente sale del metodo; los parametros que resulten insensibles se fijan y no se
presentan como ajustables.

## Decisiones fijadas antes de ajustar
- **Instancias:** las 240 del conjunto de desarrollo (`problems/clp/benchs/MPV/instances`), nunca las originales ni
  el conjunto ciego, que quedan para reportar.
- **Presupuesto:** el de Fast (`-T 4 -t 0.005 --milp 30`). Los limites de tiempo y tau no se ajustan: son decisiones
  de diseno, y si se ajustan libremente el ajuste tiende a subirlos.
- **Costo:** numero de contenedores (el objetivo del paper), con la solucion validada por `validate_bpp.py`.
- **Bloques:** `firstTest = eachTest = blockSize = 24`; cada bloque tiene una instancia de cada clase y tamano, para
  que ninguna configuracion se descarte por ruido con pocas instancias.
- **Los mismos parametros para Fast, Balanced y Quality.**

## Ejecucion
Requiere R con el paquete irace (`install.packages("irace")`) y BSG_BPP compilado con HiGHS. Desde la raiz:

    mkdir -p results/bpp/irace
    irace --scenario tools/irace/scenario.txt --parallel 4

Guardar junto al resultado el commit y el md5 del ejecutable. Despues: evaluar la configuracion elegida contra la
actual en las 240 instancias originales y en el conjunto ciego (tres semillas), y actualizar la Tabla 1 del paper.
