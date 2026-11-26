# Paper de bin packing 3D (BSG_BPP): estado del borrador

Registro de la estructura, la tesis y las decisiones del paper de `escritos/bpp` (`main.tex`; el PDF compilado es `main.pdf`).
Los pendientes del texto están marcados con `\pend{}` y aparecen en la lista "Pending items" al inicio del PDF.
El paper de palletización aérea (ULD) está en `escritos/paper`.

## Tesis

Los contenedores se generan con un cargador de un contenedor (BSG), guiado por beneficios por tipo de caja `v^κ` que ajusta un
squeaky wheel. Las cargas que BSG construye y descarta (harvest) amplían el pool, y un modelo de cubrimiento (sin apoyo vertical)
o de partición (con apoyo) recombina el pool. El LP del pool indica cuándo no hay nada más que ganar.

## Estructura

| Sección | Archivo | Contenido |
|---|---|---|
| Resumen e introducción | `main.tex`, `introduction.tex` | problema, brecha entre metaheurísticas y generación de columnas, contribuciones |
| Trabajo relacionado | `related.tex` | heurísticas del benchmark de Martello et al., métodos basados en patrones, carga de un contenedor, squeaky wheel, trabajo reciente |
| Definición del problema | `problem.tex` | 3D-BPP con bins idénticos, orientación, apoyo vertical, cotas inferiores, instancias |
| Método | `method.tex` | BSG, construcción con beneficios, squeaky wheel, pool y harvest, recombinación (Proposición 1), extensiones |
| Experimentos | `experiments_bpp.tex` | protocolo; comparación con la literatura sin y con rotaciones; ablación; comportamiento de la recombinación; conjunto ciego; apoyo vertical; límites; discusión |
| Conclusiones | `conclusions.tex` | |
| Apéndices | `appendix_bpp.tex`, `appendix_tables.tex`, `appendix_extra.tex`, `tab_ablation.tex` | resultados por clase y tamaño, tablas de apoyo, variantes descartadas, fase de mejora |

## Qué sostiene la evidencia

1. Sin rotación el método está al nivel de los mejores totales publicados (Quality 7249.3 contra 7252 de Mahvash et al. y 7258 de BRKGA en las clases 1 y 4–8); no se afirma que sea el mejor.
2. Con rotación las tres configuraciones quedan bajo el total de Mahvash et al. en las ocho clases (9004.0, 8993.7 y 8982.3 contra 9013), con margen pequeño en las clases 2 y 3.
3. La recombinación ahorra de 9 a 17 contenedores frente al squeaky wheel con el mismo tiempo, y el efecto se mantiene en el conjunto ciego y, con rotaciones, en las clases 2 y 3.
4. Con apoyo vertical, la construcción sola usa menos contenedores que LCGA; la recombinación con partición no mejoró ninguna corrida, así que la tesis unificada se sostiene en la parte metodológica y no en un aporte medido de la partición.

## Decisiones

- Autores: Ignacio Araya y Nicolás Fuentes, en ese orden.
- Revista objetivo: C&OR, ITOR o EJOR (heurísticas).
- La fase de mejora por ruina y reconstrucción queda como opción del programa y en un apéndice; no forma parte de las tres configuraciones.
- Las instancias y los archivos de resultados no están en el repositorio: las instancias están en el Drive compartido del equipo y los resultados se mantienen privados por ahora.
- El paper describe protocolo y resultados; la bitácora de las campañas (versiones, repeticiones, archivos perdidos) no va en el texto.

## Pendiente

- Verificar `related.tex` contra los PDF de los trabajos citados (varias descripciones salen de resúmenes).
- Decidir dónde se publican los archivos de resultados (repositorio, Zenodo o suplemento) y escribirlo en la declaración de disponibilidad.
- Actualizar el costo de los criterios de apoyo y el efecto de κ con las campañas industriales sobre Instance_CG (`ind_kappa`, `ind_support`).
- Comprobar las entradas de `references.bib` escritas de memoria (DOI, páginas).
