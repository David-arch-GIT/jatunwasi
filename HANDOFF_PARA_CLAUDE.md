# Traspaso de contexto — Proyecto JatunWasi Ñawpaqay (para un chat nuevo de Claude)

Este documento resume TODO el estado del proyecto para que otro Claude Code pueda continuar sin repetir trabajo ni romper nada. Léelo completo antes de tocar nada.

---

## 1. Qué es el proyecto

Tesis de grado: recorrido VR de patrimonio colonial de **Tarata, Cochabamba (Bolivia)** en **Unreal Engine 5.7**, para **Meta Quest 2 autónomo** (renderizado forward móvil). El usuario NO programa ni modela; necesita explicaciones simples y, para trabajo manual en el editor, instrucciones clic por clic. Todo en español.

- **Mapa de trabajo:** `/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN`
  (Windows: `C:\UnrealProjects\JatunWasiNawpakay\Content\JWN\MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap`)
- **Zonas:** Plaza de Tarata (inicio), Hacienda (2 plantas, museo interior), Convento (claustro con arcada), Templo (San Juan de Dios), y caminos de bosque que las conectan.

## 2. Cómo trabajar técnicamente (IMPORTANTE)

- **Puente MCPUnreal (plugin de proyecto, puerto 8090).** Para ejecutar Python en el editor:
  `curl -s -m 90 -X POST http://127.0.0.1:8090/api/editor/execute_script -H "Content-Type: application/json" -d "{\"script\":\"exec(open(r'RUTA.py').read())\"}"`
  El `execute_script` NO devuelve stdout: el script debe **escribir su resultado a un JSON** en `C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\` y luego se lee ese archivo localmente.
- **Capturas:** endpoint `http://127.0.0.1:8090/api/editor/capture_viewport` con `{"output_path":"..."}`. Antes, posicionar cámara con un script helper (ver `Scripts_Tesis\16_helper_captura_camara.py`, lee `cap_params.json` con x,y,z,p(itch),yaw y activa game view). Capturar DOS veces con ~2s de espera (la primera usa el frame viejo).
- **Límites de Python en UE 5.7 (comprobados):**
  - NO puede crear ni conectar nodos de Blueprint. NO puede leer el Event Graph. (Para BP, dar instrucciones clic por clic al usuario.)
  - `create_asset` devuelve None si el nombre quedó "atascado" → usar nombres frescos.
  - Fog color = `fog_inscattering_luminance`. `set_minimum_lod_for_platform('',N)`. `editor_set_game_view(True)` oculta gizmos.
  - Para deseleccionar antes de capturar: `EditorActorSubsystem.set_selected_level_actors([])`.
  - En bash local NO hay `python3`. Evitar heredocs con comillas raras (rompen). Para escribir scripts largos, usar la herramienta Write, no heredoc.
- **Convención de scripts (REGLA del usuario):** todo `.py` nuevo se guarda en `C:\UnrealProjects\JatunWasiNawpakay\Scripts_Tesis\` con **prefijo numérico** (van por el 39; el siguiente es `40_`) y **cabecera** obligatoria:
  ```
  # Proyecto: JatunWasi Nawpaqay - Tesis de grado
  # Fecha de uso:
  # Que hace este script:
  # Por que se necesito:
  # Resultado obtenido:
  ```
  Guardarlo ANTES de ejecutarlo. NUNCA borrar scripts del proyecto (en una sesión se borraron ~30-40 con `rm -f *.py` y son irrecuperables). Índice en `Scripts_Tesis\INDICE_SCRIPTS.md`.

## 3. REGLAS ABSOLUTAS (no negociables)

- **NO TOCAR NINGUNA LUZ:** ni posición, ni intensidad, ni radio, ni color, ni las globales (EV100 0.0, SkyLight 0.22, Luna 0.7, Bloom 0.32), ni las temperaturas (interiores cálidos 2100–2600K). El usuario recolocó a mano las luces interiores y ese es el estado bueno. Si una optimización requiere tocar una luz, SÁLTALA y avísale.
- **NO tocar props de iluminación** (faroles, apliques, velas, candelabros) ni sus materiales emisivos: no mover, no borrar, no cambiar material.
- **Solapamiento máximo 4 luces por punto:** límite de hardware del Quest 2 (forward). Intocable.
- **Cero sombras en point/spot** (solo la luna direccional). Nada de Volumetric Fog, Lumen, Rect Lights, IES, SSR, SSAO, RTC en SkyLight, Bloom>0.6.
- **No hornear iluminación** (mallas GLB sin UV de lightmap).
- Trabajar por zonas; verificar tras cada cambio; entregar capturas a altura de ojos sin guías del editor.

## 4. Estado actual de la iluminación

- **Total: 111 luces** (109 point/spot + 1 MoonLight direccional + 1 SkyLight). Solapamiento ≤4 en todas las zonas. Cero sombras en point/spot.
- **Perillas globales:** actor `PP_Master_Noche` (Unbound, exposición bloqueada min=max EV100=0.0, Bloom 0.32), `SkyLight` 0.22 azul, `MoonLight` 8000K 0.7.
- **Materiales emisivos:** `/Game/JWN/Lighting/` → `M_EmisBase` + instancias `M_Emis_FarolCalido` (5.0), `M_Emis_Vela` (2.0), `M_Emis_Brasa` (1.5), `M_Emis_Ventana`. Carpetas de luces en el World Outliner: `Luces_Plaza / Caminos / Hacienda / Convento / Templo`.
- **Hacienda (re-iluminada por radios pequeños que dejaban salas oscuras, luego el usuario la recolocó a mano):** salas con luces anchas (radios 550–850). NO tocar.

## 5. Estado de optimización para Quest 2

- **Texturas:** las 164 que pasaban de 2K están limitadas a 2048 (propiedad `max_texture_size`). Ahorro ~1.7 GB de memoria de textura.
- **LODs:** generados en las 172 mallas que no tenían. Árboles con impostor en el último LOD.
- **Corte de distancia al follaje (ISM):** GENEROSO por categoría (tras la 1ª prueba en Oculus, donde el horizonte salía plano). Suelo/árboles/cercas = nunca se cortan (0), rocas 25000, arbustos/jardines/plantas 15000, pasto 8000. Si los fps bajan, se puede acercar SOLO pasto y arbustos, nunca los árboles.
- **Cull Distance Volume:** NO usar. Se probó y ocultaba la arquitectura lejana (edificio de fondo de la Plaza). Retirado.
- **Sin merge de mallas, sin bajar densidad de follaje** (decisiones que las toma el usuario).
- **Duplicado detectado, NO borrado:** `PLZP_CanastaChuno` y `PLZP_CanastaChuno_Fix` en (0,0,0). Pendiente decisión del usuario.
- **Ajustes de proyecto (correctos):** Mobile HDR OFF, Forward Shading ON, MSAA (AA=3), Instanced Stereo ON, Mobile Multi-View ON.

## 6. Locomoción VR (BP_XRPawn)

- **Ruta:** `/Game/XRFramework/Blueprints/BP_XRPawn`. El pawn NO tiene cápsula de colisión: se mueve por **proyección a NavMesh** (el NavMesh lo contiene en el recorrido).
- **Probada en Oculus: cómoda.**
- **Estado (verificado por cadenas del .uasset, no por el grafo):** existen los nodos de la cadena de AVANCE (IA_Move / EnhancedInput, Get Forward Vector, Get World Delta Seconds, Multiply, Add Vector, Get Actor Location, Project Point to Navigation, Set Actor Location). **FALTA `Get Right Vector`** → no hay desplazamiento lateral (strafe). No se puede confirmar por script si los nodos están CONECTADOS ni si compila.
- **Cómo terminar el lateral (el usuario lo hace a mano):** del nodo `IA_Move` pin `Action Value` → `Break Vector 2D` (X=lateral, Y=adelante); `Camera → Get Right Vector`; `Right × X × (Delta×250)`; sumarlo al vector de avance antes del `Add` con `Get Actor Location`. El truco Z=0 no es imprescindible en el Right (su Z ≈ 0). Recordar Compile + Save.
- **Recomendación de tesis:** el avance direccional simple (sin strafe) es defendible en VR. Prioridad mayor que el strafe: giro cómodo (snap turn) y viñeta al moverse para reducir mareo.

## 7. Puertas de la Hacienda (arreglado)

Las puertas bloqueaban porque el NavMesh no conectaba a través de los vanos (peor en 2º piso por colisión "default"). Se puso la colisión de los muros del 2º piso (`HACV7_EXP_ExteriorWalls_Upper`) en **complejo (Complex As Simple)** y se **reconstruyó el NavMesh** (`RebuildNavigation`). Verificado: 4/4 rutas de prueba que cruzan puertas dan camino navegable válido. Hay `HAC_NavBounds` cubriendo la Hacienda.

## 8. Rutas exactas

| Cosa | Ruta |
|---|---|
| Mapa de trabajo | `Content\JWN\MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap` (`/Game/JWN/...`) |
| Backup del estado bueno del usuario | `..._BACKUP_LUCES_USUARIO.umap` |
| Otros backups | `..._BACKUP_LUCES_FINAL` (105 luces auto), `..._BACKUP_PRE_LUCES` |
| Materiales emisivos | `Content\JWN\Lighting\` (`/Game/JWN/Lighting/`) |
| BP_XRPawn | `Content\XRFramework\Blueprints\BP_XRPawn.uasset` |
| Bitácora técnica (prosa) | `C:\UnrealProjects\JatunWasiNawpakay\BITACORA_TECNICA.md` |
| Scripts de Python + índice | `C:\UnrealProjects\JatunWasiNawpakay\Scripts_Tesis\` |
| Volcados JSON de trabajo | `C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\` |
| APK al empaquetar | `C:\UnrealProjects\JatunWasiNawpakay\Saved\StagedBuilds\Android_ASTC\` |
| Respaldo a disco externo | `.uproject` + `Content\` (14 GB) + `Config\` + `Plugins\` + `BITACORA_TECNICA.md`. NO copiar Intermediate/DerivedDataCache/Binaries/External/Saved. |

## 9. Empaquetado (lo hace el usuario; a Claude lo desconecta)

1. Edit → Plugins → **MCPUnreal** → desmarcar Enabled → Restart (esto corta el puente 8090; obligatorio o el cook falla).
2. Verificar Android/ASTC (SDK ya configurado con SetupAndroid; Min SDK 29+, compresión ASTC).
3. Platforms → Android (ASTC) → Package Project.
4. APK en `Saved\StagedBuilds\Android_ASTC\`. Si falla: Output Log / `Saved\Logs\`.
5. Reactivar MCPUnreal (Plugins → Enabled → Restart) para que Claude siga.

## 10. Pendientes

- Cablear el ramal LATERAL de la locomoción a mano en BP_XRPawn (sección 6).
- Medir fps reales en el visor (`stat unit`, `stat fps`, `stat rhi`) tras el follaje generoso; si <72 en la Plaza, acercar corte de pasto/arbustos (no árboles).
- Decidir si se borra el duplicado `PLZP_CanastaChuno_Fix`.
- (Opcional) confort VR: snap turn + viñeta al moverse.

## 11. Lecciones / trampas (para no repetir errores)

- **Backups:** al "actualizar el backup" se llegó a sobrescribir el estado denso de 141 luces con uno de 59. Recuperado desde autosave (`Saved/Autosaves`). SIEMPRE hacer el backup con nombre nuevo antes de cambios grandes; no sobrescribir el único bueno.
- **Cull Distance Volume:** oculta arquitectura lejana. No usar; usar corte por objeto/ISM con distancias generosas.
- **Cortes de follaje agresivos:** vacían el horizonte. Árboles/suelo nunca se cortan (los árboles tienen impostor barato).
- **Scripts borrados:** nunca `rm -f *.py` sobre la carpeta de trabajo; se perdieron scripts de la primera mitad de la iluminación.
- **La métrica "218 millones de triángulos"** era LOD0×instancias (peor caso estático), no lo que se dibuja por frame. Medir de verdad en el visor.
- **Memoria persistente de Claude** para este proyecto: hay archivos de memoria (unreal-execution-channel, night-lighting-state, hacienda-state, scripts-tesis-convention, etc.) que un chat nuevo con la misma memoria ya verá; este documento los complementa.
