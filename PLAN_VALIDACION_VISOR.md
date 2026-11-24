# Validación en visor antes de la defensa (actualizado 2026-11-24, noche)

## Qué se arregló esta noche (con evidencia)
| Problema | Causa real | Arreglo | Verificado |
|---|---|---|---|
| **No deja moverse** (y botón A / gatillo del pozo sin efecto) | En UE 5.7, con Enhanced Input, OpenXR solo entrega los controles a las *acciones*; la lectura de *teclas sueltas* que usaba la locomoción vale 0 siempre en el visor (OpenXRInput.cpp, líneas 455-481). Ayer funcionaba porque era la locomoción anterior. | Acciones nuevas `IA_JW_Mover / BotonA / Gatillo` + librería C++ `UJWEntradaVR`; reemplazados los 4 nodos de tecla en `BP_XRPawn`. | PIE inyectando por la **misma vía que OpenXR**: mueve adelante y de lado, A alterna el ambiente, el gatillo lanza la moneda. |
| Pantalla negra / app muerta | `GPU hang` solo con el perfilador de GPU en modo detallado que activé para medir | Perfilador desactivado | 6 min sin fallo; confirmar en la prueba |
| Inicio mirando de lado | `PlayerStart_Inicio` yaw -118° | Yaw -100°: Adela a 8.6° a la derecha y el cartel de controles a 8.2° a la izquierda, ambos a ~2.8 m | Medido en el mapa |
| Retablo dorado gris en el visor | 3 materiales no compilaban para Android | Corregidos (0 materiales fallidos en el empaquetado) | Log del empaquetado |
| 90 Hz | El visor elige 90 Hz | `setprop debug.oculus.refreshRate 72` | 72/72 FPS |

## Prueba de mañana (unos 10 minutos)
1. Visor **cargado** (≥ 50 %) y conectado por USB a la PC.
2. Instalar el APK final: `Scripts_Tesis\496_visor_instalar_y_medir.ps1 -Minutos 1` (instala + modo quiosco).
3. `adb shell setprop debug.oculus.refreshRate 72` y `ovrgpuprofiler -d`.
4. Abrir la app desde el visor; registro: `497_visor_registrar_recorrido.ps1 -Phase iniciar`.
5. Visor puesto: **moverse con la palanca derecha**, girar con la izquierda, **A** (ambiente), apuntar a una cartela, seguir a Adela hasta el Templo.
6. `497 -Phase resumen` → FPS por minuto, tramos lentos, cierres.
7. Si todo bien: recorrido completo + prueba de transmisión por cable (`Escritorio\Ver_Visor_en_TV.bat`).

## Comandos del día de la defensa (con la PC/laptop y el cable)
- `adb shell setprop debug.oculus.refreshRate 72`
- `adb shell am broadcast -a com.oculus.vrpowermanager.prox_close`
- `adb shell settings put system screen_off_timeout 7200000`
- Transmisión sin WiFi: `Escritorio\Ver_Visor_en_TV.bat` (scrcpy por cable → HDMI a la tele).
- Si al empezar no ves a Adela de frente: mantener pulsado el botón Meta para recentrar la vista.

## Pendiente (con el visor y medición)
- Fluidez: 65/72 FPS en la plaza (GPU 98 %). Reducir sobredibujado (domos del cielo y vegetación recortada) **midiendo en el visor**, no a ciegas.
