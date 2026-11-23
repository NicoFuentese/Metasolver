# Bosquejo del paper de bin packing 3D (BSG_BPP)

> **Estado:** la estructura de §3 ya está implementada en los `.tex` de esta carpeta (introduction, related,
> problem, method, experiments_bpp, conclusions y apéndices). Los pendientes están marcados en el texto con
> `\pend{}` y listados al inicio del PDF (`main.pdf`, "Pending items"). Este archivo queda como registro de
> las decisiones.

Propuesta de estructura para convertir el borrador de `escritos/bpp` (hoy: Method + Experiments + apéndice,
31 páginas, de las cuales unas 20 son experimentos) en un paper publicable, y lista de lo que falta para
que sea consistente. Las decisiones marcadas con **[D]** son de los autores.

## 1. El problema del borrador actual

- No tiene introducción, revisión de literatura, definición del problema ni conclusiones: empieza en
  Method y termina en una discusión de los límites de la evidencia.
- La sección de experimentos (~870 líneas) es el doble de Method y cuenta la historia del proyecto
  (campañas anteriores, archivos perdidos, prototipo en Python, deriva entre campañas) en vez de responder
  preguntas. Las advertencias se repiten en el setup, en los resultados y en la discusión.
- No hay una tesis explícita (resuelto en §2). Los resultados más fuertes (rotaciones, industriales) no usan o usan poco el
  componente que el título destaca (la recombinación), y el más débil (sin rotación, +4 a −3 contenedores
  frente a Mahvash) es el que se presenta primero.

## 2. Tesis (decidida: tesis unificada)

> Los contenedores se generan con un cargador de un contenedor (BSG) que respeta cualquier restricción de
> carga, guiado por beneficios por tipo de caja que ajusta un squeaky wheel; las cargas que BSG ya construye
> (harvest) amplían el pool, y un modelo de cubrimiento (sin apoyo vertical) o de partición (con apoyo)
> recombina el pool. El LP del pool indica cuándo dejar de recombinar.

La misma tubería se aplica a los dos escenarios; solo cambian las restricciones que respeta BSG y el modelo
de recombinación:

| | Martello et al. (sin apoyo) | Industriales (70 % de apoyo) |
|---|---|---|
| Cargador | BSG | BSG con el criterio de área |
| Squeaky wheel + harvest | sí | **falta medirlo** (hoy: construcción sola para n ≥ 500) |
| Recombinación | cubrimiento: se sacan las cajas sobrantes | partición: no se saca ninguna caja (`--partition`) |
| Proposición 1 (cota del LP y poda) | vale (duales ≥ 0) | vale (duales libres; la demostración usa la igualdad) |

Mensajes que la evidencia sostiene o debe sostener:
1. **Calidad–tiempo sin apoyo**: Fast (6.7 s/instancia) obtiene 7256.7 contra 7258 de BRKGA (hasta 130 s
   en otra máquina); Quality (100 s) obtiene 7249.3, bajo Mahvash (7252). Falta normalizar los tiempos (§4.C).
2. **Rotaciones**: Quality obtiene 8985.3 contra 9013 de Mahvash (−0.31 %). Repetir con archivos crudos.
3. **Recombinación con prueba**: el LP demuestra en ~95 % de las corridas que el incumbente es el mejor del
   pool; la recombinación ahorra 10–13 contenedores frente al squeaky wheel a igual tiempo en muestras
   independientes del diseño.
4. **Generalidad**: con apoyo vertical, la misma tubería (con partición) se compara con LCGA (−5.9 % con la
   construcción sola). Falta la evidencia de que el squeaky wheel y la partición aportan o al menos no
   empeoran a igual tiempo (§4.F).

Revista objetivo **[D]**: C&OR, ITOR o EJOR (sección de heurísticas). La tesis unificada (método general
para restricciones de carga) es más atractiva para EJOR si el punto 4 queda respaldado.

## 3. Estructura propuesta (~25 páginas + apéndice)

| § | Sección | Contenido | De dónde sale |
|---|---|---|---|
| 1 | Introduction | Problema y relevancia; brecha: los métodos de generación de columnas generan patrones con duales y pricing caro, las metaheurísticas no recombinan contenedores; contribuciones (3–4 viñetas); resumen de resultados | Nuevo. Reutilizar el estilo de `escritos/paper/introduction.tex` |
| 2 | Related work | 2.1 Heurísticas para 3D-BPP (TS de Lodi, GLS de Faroe 2003, TS2P/GVND de Parreño 2010, BRKGA de Gonçalves 2013, SD de Zhu 2012, otras recientes); 2.2 Generación de columnas y set covering (Monaci y Toth 2006, Mahvash 2018, Elhedhli 2019); 2.3 Squeaky wheel; 2.4 BSG y el problema de carga de un contenedor (Araya 2014, 2017, Guesser 2026); 2.5 Soporte vertical | Nuevo. Partir de `escritos/paper/literature.tex` y de la §"Relation to previous work" de `method.tex`. La mayoría de las referencias ya están en `references.bib` |
| 3 | Problem definition | 3D-BPP con contenedores idénticos, orientación fija o 6 rotaciones; variante con 70 % de apoyo; cotas inferiores (continua, L1, L2 de Martello et al.) | Hoy repartido entre "Notation" y "Rotations and vertical support" |
| 4 | Method | 4.1 Visión general (fig. 1); 4.2 BSG para un contenedor (resumido, citar); 4.3 Construcción con beneficios v^κ; 4.4 Squeaky wheel; 4.5 Pool y harvest; 4.6 Recombinación (Proposición 1, algoritmo, reparación); 4.7 Extensiones (rotaciones, soporte) | `method.tex` casi tal cual. Mover la fase de mejora por ruina y reconstrucción a un apéndice, o eliminarla si se elimina el párrafo de instancias industriales pequeñas |
| 5 | Computational experiments | Ver tabla de abajo | `experiments_bpp.tex`, condensado |
| 6 | Conclusions | Qué se logra, límites (escala a cientos de cajas, incompatibilidad con soporte), trabajo futuro (generación guiada por duales con más presupuesto, modelo de partición compatible con soporte) | Nuevo; partes de "Discussion and limits of the evidence" |
| A | Results per class and size | Tablas por celda | `appendix_bpp.tex` |
| B | Variants that did not improve | Tabla de variantes descartadas | Hoy `tab:e-negative` |
| S | Material suplementario | Resultados crudos, soluciones, scripts, validadores | Repositorio |

Sección 5 propuesta, organizada por preguntas:

| § | Pregunta | Evidencia | Estado |
|---|---|---|---|
| 5.1 | Setup | Instancias, máquina, protocolo (un párrafo), configuraciones, validación | Recortar "Conditions of the campaigns" a 2–3 frases cuando todas las campañas sigan el protocolo |
| 5.2 | ¿Cómo se compara con la literatura sin rotación? | `tab:e-main`, curva calidad–tiempo con tiempos normalizados | Falta normalizar los tiempos |
| 5.3 | ¿Y con rotaciones? | `tab:e-rot` | Repetir (todas las filas son †) |
| 5.4 | ¿Qué aporta cada componente? | Ablación con control a igual tiempo; harvest según presupuesto | Ablación en curso (`results/bpp/ablation_2026-11`) |
| 5.5 | ¿Cómo se comporta la recombinación? | Prueba por LP, poda, cota del pool, MILP plano contra MILP con objetivo | Existe (2.º conjunto ciego); falta medir la poda por separado |
| 5.6 | ¿Generaliza? | Clases 2–3 y conjuntos ciegos | Existe; repetir el 1.er conjunto ciego o eliminarlo |
| 5.7 | ¿Funciona la misma tubería con apoyo vertical? | `tab:e-ind`, squeaky wheel y partición a igual tiempo, costo del soporte | Falta el experimento de §4.F |
| 5.8 | Límites | Instancias grandes, cota del pool | Existe |

## 4. Lo que falta para que sea consistente

### A. Secciones que no existen
- [ ] Introduction, Related work, Problem definition, Conclusions, Abstract.
- [ ] Verificar en los PDFs cada afirmación sobre otros trabajos (tiempos, máquinas, criterios de soporte de
      LCGA, totales de Mahvash por celda). Hoy varias vienen de "nuestra lectura de sus tablas".

### B. Campañas sin archivos crudos (marcadas con †)
- [ ] Ablación (en curso, 3 semillas, con control `swo_T26` a igual tiempo).
- [ ] Rotaciones: Fast, Balanced, T=33, Quality y squeaky wheel solo, en las 320 instancias.
- [ ] Primer conjunto ciego (los archivos de las instancias tampoco se guardaron): repetir con el segundo o
      eliminarlo del texto.
- [ ] Fila del prototipo en Python (`tab:e-milp`) y "Time limit of the MILP": rehacer con la implementación en C++.
- [ ] Los resultados de la campaña de noviembre (Fast, Balanced, Quality) que el texto dice "stored" no
      están en `results/bpp` del repositorio: subirlos.
- [ ] Variantes descartadas: aceptar que se corrieron con versiones anteriores (dejarlas en el apéndice B
      con esa advertencia) o repetir las dos que se destacan en el texto.

### C. Comparación justa
- [ ] Normalizar los tiempos de BRKGA, SD y LCGA en el 3D-BPP sin rotación (PassMark single-thread, como ya
      se hace en los industriales) y marcarlos en la curva calidad–tiempo.
- [ ] Mahvash no reporta tiempos sin rotación: decirlo en la tabla y no basar la tesis en esa comparación.
- [ ] Pedir a los autores resultados por instancia (Gonçalves, Mahvash) para poder hacer pruebas pareadas;
      si no los hay, dejar explícito que la comparación es por totales.
- [ ] Separar en el texto las pruebas confirmatorias (muestras independientes del diseño) de las
      exploratorias, o corregir por comparaciones múltiples (Holm).

### D. Notación (choques de símbolos en `method.tex`)
- [ ] `T` es a la vez el número de tipos de caja y el límite de tiempo del squeaky wheel.
- [ ] `t` es a la vez el índice de tipo y el tiempo de BSG por contenedor.
- [ ] `ρ` es a la vez el aumento de peso del squeaky wheel y la fracción de ruina de la fase de mejora.
- [ ] `p` es el parámetro de contacto de VCS y `p_t` el beneficio de un tipo.
- [ ] Unificar los nombres de las configuraciones (Fast/Balanced/Quality en el paper, F5/H20/B100 en el
      README y en la bitácora).

### E. Texto y código que no coinciden
- [ ] Harvest: el texto dice que los candidatos se acotan a 8K; el código recorta a K cuando pasan de 8K.
- [ ] Harvest: el texto dice que actúa solo en las construcciones; también actúa en `--scratch` y en la
      transferencia parcial de la fase de mejora.
- [ ] Algoritmo 4: la recombinación corre solo si |S*| > LB; el código la corre siempre (costo despreciable,
      pero el texto debe coincidir).
- [ ] Tiempo: el texto dice wall-clock porque `clock()` en Windows mide tiempo real; en Linux mide CPU. Usar
      `std::chrono::steady_clock` o decirlo.
- [ ] Comentario de `milp_target` que menciona una restricción `sum(x) <= UB-1` que el modelo no tiene.
- [ ] Duales: el código invierte el signo y recorta los negativos sin recalcular z; verificar que no afecte
      la poda (Proposición 1 supone duales óptimos).
- [ ] El LP del pool no tiene límite de tiempo y puede pasarse de T_milp.
- [ ] La verificación final (`check`) no revisa el apoyo vertical, aunque el texto dice que la solución se
      verifica caja por caja; el validador de apoyo (en Python) no está en el repositorio.

### F. Instancias industriales (necesario para la tesis unificada)
- [x] Modelo de partición en C++ (`--partition`, compatible con `--support`). Probado en instancias de
      Martello con `--support area`: soluciones válidas y todas las cajas apoyadas. La verificación interna
      (`check`) ahora revisa también el apoyo por área.
- [ ] Subir al repositorio las 160 instancias industriales (y las 72 adicionales), su convertidor y el
      validador de apoyo.
- [ ] Experimento a igual tiempo en las 80 instancias con n ≥ 500 (apoyo 70 %, κ=1): construcción sola con
      t=2 s (~18 s) contra squeaky wheel con t=0.2 s y t=0.5 s y T=18 s, con y sin `--partition`; repetir con
      un presupuesto de ~60 s. Si el squeaky wheel no compensa la pérdida por bajar t, decirlo y explicar
      por qué (una construcción ya cuesta 18 s).
- [ ] Partición en las industriales con n < 500 (hoy 112 contra 112 sin ganancia, con el prototipo).
- [ ] Reescribir en `method.tex` el párrafo "Vertical support" y la reparación: hoy dicen que la recombinación
      es incompatible con el apoyo; pasa a ser "con apoyo se usa la partición". Extender la Proposición 1 al
      caso de igualdad (duales libres) en una línea.
- [ ] La fase de mejora (ruina y reconstrucción) solo se usa en las industriales pequeñas: si el squeaky wheel
      con partición la iguala, eliminarla del método.
- [ ] No se pudo verificar que las instancias sean las de Elhedhli et al.: pedirlas a los autores.
- [ ] El criterio de soporte de LCGA es distinto (tolerancia de 5 mm, soporte no exigido a todas las cajas):
      decir que el nuestro es más estricto o comparar con el mismo criterio.

### G. Reproducibilidad
- [ ] Un script por tabla y figura que lea los resultados crudos (hoy el encabezado de
      `experiments_bpp.tex` dice que las cifras salen de AGENTS.md y del README, es decir, transcritas a mano).
- [ ] Guardar commit y md5 del ejecutable junto a cada campaña (las campañas antiguas sí lo hacen:
      `exp2_commit.txt`, `mpv_v1_commit.txt`).
- [ ] En `results/bpp/mpv_v1_T30_sol`, 5 de las 240 soluciones guardadas tienen un contenedor menos que el
      CSV (son de la reejecución por SIGPIPE): regenerar el CSV o las soluciones para que coincidan.
- [ ] README de reproducción con un comando por campaña.
- [ ] Agregar `\usepackage{lmodern}` a `main.tex` (sin él, TeX Live genera fuentes en mapa de bits).

### H. Parámetros
- [ ] κ, ρ, σ, la fracción 0.1, θ y K se eligieron con las instancias originales: decirlo en un solo lugar
      y reportar la sensibilidad de ρ (hay datos en `results/bpp/F_rate01.csv` y `G_rate06.csv`).
- [ ] Justificar por qué Quality no usa harvest (hoy la evidencia es una sola semilla).

## 5. Orden de trabajo sugerido

1. ~~Decidir la tesis~~ (unificada); decidir la revista (**[D]**).
2. Terminar la ablación y repetir las rotaciones con el protocolo; subir los resultados de noviembre;
   subir las instancias industriales y correr el experimento de §4.F.
3. Corregir notación y discrepancias código–texto (§4.D, §4.E).
4. Scripts de tablas y figuras desde los resultados crudos.
5. Escribir Introduction, Related work, Problem definition y Conclusions.
6. Condensar la sección 5 según la tabla de §3 y mover las variantes descartadas al apéndice.
