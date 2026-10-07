# Plan de tareas — Jatun Wasi
*Tablero simple. Mantener fechas. Al mover a "Hecho", anotar la fecha y el build/commit asociado.*

## Hecho
- [x] Navegacion verificada (5 rutas find_path validas) — 2026-10-03 — build SPAWN_ARREGLADO
- [x] Fix critico de spawn (PlayerStart flotante -> plaza) — 2026-10-03 — script 360 / APK
- [x] Guia de controles sobre foto real Quest 2, colocada en plaza, auto-cierre 30s — 2026-09-30/10-03
- [x] Optimizacion Quest (bosque, Nanite fallback, config) — 2026-09-22
- [x] Version 2 en git (rama) — 2026-10-03 — commit f72cd96
- [x] Relieve natural de bosque (rocas/troncos/helechos/arbustos por PCG instanciado, exclusion NavMesh, culling 70m) — 2026-10-03 — 3659 piezas + peniascos grandes + suelo texturizado (MI_JW_Ground_Earth_V3) — scripts 361-365 — pendiente test en visor

## En curso
- [x] Contencion del avance con palanca — HECHA 2026-10-06 (correa NavMesh en BP_XRPawn, conserva caminar+teletransporte) — pendiente test en visor
- [ ] Registro de tiempos/defectos/mediciones (sistema iniciado 2026-10-03; mantener en cada tarea)

## Pendiente
- [ ] Subir rama Version 2 a GitHub (requiere OK del usuario)
- [ ] Cuestionario/encuesta web: preguntas de contenido (puntuacion) + metricas de experiencia + panel
- [ ] Guia IA "Adela Zamudio" (requiere plugin + API key + modelo 3D)
- [ ] Animacion de baile 2o piso hacienda + musica de epoca
- [ ] Re-medir rendimiento (draw calls/texturas/tris/FPS) citando archivo de evidencia
- [ ] Decisiones de tesis (las define el chat del documento): DSRM si/no, numero de usuarios para pruebas, tratamiento de "difusion" en las variables

## Notas
- Al cerrar cada hito: build numerado en Entrega_Quest + commit en rama de version.
- Requisitos del proyecto: salieron del diagnostico (encuesta), no de un cliente externo. No inventar rol de cliente para el tutor.
