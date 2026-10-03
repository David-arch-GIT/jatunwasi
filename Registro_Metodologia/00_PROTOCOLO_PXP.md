# Protocolo de desarrollo y registro — Jatun Wasi
### Metodología: PXP adaptado (Personal Extreme Programming), desarrollo individual
*Iniciado: 2026-10-03. Fija CÓMO se trabaja y se registra desde esta fase, para sostener la metodología ante el jurado con evidencia real y verificable.*

---

## 1. Marco (con cautela de fuentes)
PXP = Extreme Programming adaptado a un **solo desarrollador** + medición estilo **PSP**.
Fuentes: Agarwal & Umphress (2008); guías de implementación Dzhurov et al. (2009); revisión Iyawa (2020, AMCIS).

> **REGLA CERO INVENCIÓN:** la lista EXACTA de las prácticas de PXP debe tomarse del **paper original** (Agarwal & Umphress 2008 / Dzhurov 2009). **No se transcribe aquí** para no inventarla. Este protocolo describe nuestra práctica real y la mapea a las categorías generales de XP/PSP. El redactado formal de las prácticas lo hace el chat del documento **con el paper en mano**.

PXP ya contempla que un desarrollador individual **no aplique todo** (sin programación en pareja, código propio, estándar propio). Iyawa (2020) reporta como limitaciones reales: **mayor probabilidad de errores** y **falta de diversidad de habilidades**. Esto se declara, no se oculta.

---

## 2. Prácticas y evidencia (tabla honesta — preliminar)
| Práctica (categoría general) | Estado | Evidencia |
|---|---|---|
| Entregas pequeñas y frecuentes | Aplicada | APK numerados y fechados (`Entrega_Quest/`) |
| Diseño incremental por fases | Aplicada | `AGENTS.md` (validar zona antes de la siguiente) |
| Refactorización | Aplicada | Kit hacienda rehecho, instancing, re-optimización |
| Estándar propio de código/proceso | Aplicada | 361 scripts numerados `Scripts_Tesis/` + `AGENTS.md` |
| Pruebas continuas (manuales) | Aplicada (parcial) | 1 100+ capturas + prueba PIE por fase. **No automáticas** |
| Medición de tamaño (PSP) | Aplicada (a reforzar) | `registro_mediciones.csv` (cada cifra → su archivo) |
| Registro de defectos | Aplicada | `registro_defectos.csv` |
| Control de versiones | Parcial | 2 versiones git (V1 en GitHub, V2 local) |
| **Registro de tiempo por tarea (PSP)** | **Iniciado 2026-10-03** | `registro_tiempos.csv` |
| Pruebas automáticas (TDD) | No aplicada | — (se declara como limitación) |
| Programación en pareja / cliente presente / propiedad colectiva | No aplicable | Proyecto individual |

> El veredicto FINAL (SÍ/PARCIAL/NO por práctica) lo fija el chat del documento con el paper.

---

## 3. Rutina por cada tarea (desde ahora)
1. **Antes:** anotar la tarea en `plan_tareas.md` (estado "en curso") y la **hora de inicio** en `registro_tiempos.csv`.
2. **Medir inicio** (si aplica: tris / draw calls / FPS / conectividad) y guardar el archivo de evidencia (JSON/captura) → anotar en `registro_mediciones.csv` (columna *Antes* + *Archivo*).
3. **Desarrollar.**
4. **Verificar por fase:** captura de viewport + prueba PIE/visor (regla `AGENTS.md`). Guardar la captura.
5. **Defecto encontrado →** registrarlo en `registro_defectos.csv` (cómo se detectó, causa, corrección, evidencia).
6. **Medir fin** → `registro_mediciones.csv` (columna *Después* + *Archivo*).
7. **Después:** **hora de fin** en `registro_tiempos.csv`; mover la tarea a "hecho" en `plan_tareas.md`.
8. **Al cerrar un hito:** build numerado (`Entrega_Quest/`) + **commit en rama de versión**.

---

## 4. Cómo pedirme las tareas (para que queden documentadas)
Tú pídeme la tarea normal; **yo me encargo** de registrar tiempo, defectos, mediciones y de actualizar el plan en cada una. Si quieres reforzarlo, usa esta plantilla:

> **Tarea:** [qué] · **Fase:** [zona/etapa] · *Mide antes y después y guarda el archivo* · *Verifica con captura/PIE* · *Registra defecto y tiempo.*

---

## 5. Limitaciones declaradas (honestas, para el jurado)
- Verificación **manual** y por fases (captura + PIE), **no** pruebas automáticas/TDD.
- Registro de **tiempo por tarea** iniciado en esta fase (oct-2026), **no** desde el día 1 del proyecto.
- Un solo desarrollador: mayor riesgo de errores y menor diversidad de habilidades (Iyawa, 2020).
- Mediciones de rendimiento previas (draw calls/texturas/tris) **provienen de registro de trabajo y faltan re-medir citando archivo** (ver `registro_mediciones.csv`).
