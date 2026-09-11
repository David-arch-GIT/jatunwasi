# Índice de scripts — JatunWasi Ñawpaqay (Tesis de grado)

Carpeta: `C:\UnrealProjects\JatunWasiNawpakay\Scripts_Tesis\`

Contiene los scripts de Python realmente ejecutados en el proyecto. Los numerados (01–33) son la sesión de iluminación y optimización, en orden cronológico de uso, cada uno con cabecera. La subcarpeta `Anteriores\` guarda scripts de fases previas (modelado en Blender, entorno, utilidades) tal como estaban. Al final se listan los scripts que **no se pudieron recuperar**.

Regla vigente: todo script nuevo se guarda aquí, numerado y con cabecera, antes de ejecutarse.

## Scripts de la sesión de iluminación y optimización (01–33)

| Nº | Archivo | Qué hace | Resultado |
|---|---|---|---|
| 01 | inventario_luces_completo.py | Vuelca todas las luces y perillas a JSON | Inventario completo generado |
| 02 | verificar_apliques_camino.py | Cuenta apliques y luces de camino | Detectó apliques duplicados |
| 03 | detalle_duplicados_apliques.py | Detalla cada aplique (luz/malla, posición) | Duplicados repartidos, no apilados |
| 04 | conteo_total_solapamiento.py | Cuenta luces y solapamiento por zona | 141 luces, solape 12 en la Hacienda |
| 05 | adelgazar_luces_a_59.py | Reduce 141→59 protegiendo canónicas | 59 luces, todas ≤4 (quedó escaso) |
| 06 | backup_mapa.py | Duplica el mapa a un backup | Backup creado |
| 07 | inspeccionar_bp_xrpawn.py | Localiza e inspecciona BP_XRPawn | Ruta hallada; Python no lee el grafo BP |
| 08 | buscar_autosave.py | Ve si el autosave es direccionable | No estaba en el Content |
| 09 | cargar_autosave_141.py | Carga el autosave con las 141 luces | Cargadas 141 luces, 0 sombras |
| 10 | reparar_141_a_105.py | Reduce radios y quita hasta ≤4 sin borrar canónicas | 105 luces, todas ≤4 |
| 11 | transferir_a_mapa_trabajo.py | Traspasa el mapa reparado al de trabajo | Mapa de trabajo con 105 luces |
| 12 | diagnostico_estado_mapa.py | Diagnostica el mapa cargado | Confirmado 105 luces, sin pérdida |
| 13 | ping_editor.py | Ping simple al editor | Editor respondía |
| 14 | ping_editor_robusto.py | Ping con captura de error | Estado confirmado |
| 15 | verificar_limpiar_backup.py | Verifica, borra recover, backup | 105 luces, backup actualizado |
| 16 | helper_captura_camara.py | Coloca cámara y game view para capturar | Helper de capturas reutilizable |
| 17 | audit_texturas_lods.py | Audita texturas >2K y mallas sin LODs | 164 texturas >2K, 172 sin LODs |
| 18 | audit_drawcalls_tris.py | Audita draw calls, tris, culling, tick | Follaje = principal costo; 630 sin culling |
| 19 | audit_tick_materiales.py | Audita tick real y blend modes | 0 tick real; 7 masked, 12 translúcidos |
| 20 | opt_texturas_2k_cull_follaje.py | Texturas a 2K + corte de follaje ISM | −1757 MB textura; 229 ISM con corte |
| 21 | opt_generar_lods.py | Genera LODs en mallas sin LODs | 172 mallas con 3–4 LODs |
| 22 | opt_cullvolume_impostores.py | Cull volume + impostores + decal/glow | Impostores OK; 105 luces intactas |
| 23 | opt_lods_pcg_medir_tris.py | LODs al follaje PCG + mide tris | Medición estática poco fiable |
| 24 | opt_apretar_cull_medir_tris.py | Aprieta corte + mide tris por frame | Camino −85%; métrica no concluyente |
| 25 | quitar_cullvolume.py | Elimina el cull volume | Ocultaba edificio lejano; retirado |
| 26 | verificar_final_optimizacion.py | Verifica luces intactas + backup | 105 luces intactas |
| 27 | dump_luces_hacienda.py | Vuelca luces de la Hacienda por sala | Confirmó radios 350–400 en salas grandes |
| 28 | consolidar_luces_hacienda.py | Sube radios, quita duplicados hasta ≤4 | 13 luces anchas; salas iluminadas |
| 29 | verificar_hacienda_final.py | Valores finales por sala + backup | Otras zonas sin tocar |
| 30 | backup_usuario_huella_luces.py | Backup del usuario + huella de luces | Backup LUCES_USUARIO + huella 111 luces |
| 31 | cull_props_v1.py | Cull a props + verifica luces | 0 props sueltos; 111 luces idénticas |
| 32 | cull_props_v2.py | Cull a props (red amplia) + verifica | Decoración es ISM; 111 luces idénticas |
| 33 | detectar_duplicados_materiales.py | Detecta mallas duplicadas | 1 duplicado (PLZP_CanastaChuno + _Fix) |

## Scripts de fases anteriores (subcarpeta `Anteriores\`, 42 archivos)

Copiados tal cual, con el nombre aplanado según su ubicación original. No llevan cabecera porque son de fases previas y no se verificaron sus detalles en esta sesión.

- **Modelado en Blender (`Tools_BlenderPipeline_*`, `Tools_Hacienda*`, `Tools_*Plaza*`):** construcción de la Hacienda V4–V7 y sus correcciones, kit V1, y la Plaza de Tarata. Son scripts de Blender, no del editor de Unreal.
- **Entorno y suelo (`Saved_MCP_Captures_*`, `Saved_Environment_*`, `Saved_Architecture_*`):** generación del terreno, vegetación, plaza e iluminación de entorno de sesiones anteriores.
- **Utilidades (`Saved_ClaudeBackups_*`):** borrado de geometría legacy, descubrimiento de actores, auditoría de vegetación, verificación de conteos.
- **Raíz (`ue_physcheck2.py`):** verificación de física.

## Scripts que NO se pudieron recuperar

Durante esta sesión, en pasos de limpieza, ejecuté `rm -f *.py` sobre la carpeta temporal varias veces. Eso borró **de forma irreversible** los scripts de la primera mitad de la sesión de iluminación. No los reconstruyo (serían inventados). Por su función, los que faltan son:

- **Base nocturna global:** creación de `PP_Master_Noche` (exposición bloqueada), `MoonLight`, `SkyLight`, niebla y `SkyAtmosphere`.
- **Materiales emisivos:** creación de `M_EmisBase` y sus instancias `M_Emis_FarolCalido/Vela/Brasa/Ventana`.
- **Cúpula de estrellas:** `M_Stars_Sky`, `StarDome`.
- **Luces por zona:** colocación de Plaza (`LP_*`), Caminos (`LC_*` y faroles), Convento (`LCV_*`), Templo (`Spot_Retablo`, `NaveFill`, `LT_Altar`).
- **Correcciones de iluminación ("5 problemas") y solapamiento:** `fix_A.py` … `fix_H.py`.
- **Ventanas emisivas (luego descartadas):** `windows_final.py`, `del_win.py`, `win_emis.py`, `conv_win.py`, `conv_ism.py`, `warm.py`.
- **Colocación de apliques de pared:** `test1.py`, `test2.py`, `place.py`, `place2.py`, `addback.py`, `addback2.py`, `placefinal.py`.
- **Consultas y capturas auxiliares:** `query_pts.py`, `query_props.py`, `query_orb.py`, `query_orb2.py`, `scan_white.py`, `envel.py`, `ism.py`, `gather.py`, `cap_ceil.py`, entre otras.

Nota: la lógica de varios de estos (radios, intensidades, temperaturas, posiciones) quedó documentada en `BITACORA_TECNICA.md` y en la memoria del proyecto, aunque los archivos `.py` en sí ya no existen.

## Scripts de colisiones/paso (45–49) — 2026-08-27

| Nº | Archivo | Qué hace | Resultado |
|---|---|---|---|
| 45 | diag_colisiones_puertas.py | Diagnostica colisiones de Hacienda/Convento por nombre | Malla Hacienda sin colisión; arcos Convento con colisión simple |
| 46 | fix_colisiones_arcos_puertas.py | Pone Arch_Bay y Wall_Door en Complex-As-Simple + rebuild NavMesh | Arcos/puertas respetan el hueco; sin tocar visual |
| 47 | diag_hacienda_portal.py | Escaneo por cercanía de colisionadores de la Hacienda | Muros ext. ya Complex-As-Simple; "Cubes" son del 2º piso |
| 48 | test_navmesh_puertas.py | Lista NavBounds y prueba rutas afuera→adentro | Hacienda rutas válidas; Convento 1 ruta parcial |
| 49 | retest_convento_4lados.py | Reentrada al claustro por 4 lados tras rebuild | Claustro conecta por Sur/Norte/Este ✅ |

## Scripts de apariciones 3D (50–60) — 2026-08-27

| Nº | Archivo | Qué hace | Resultado |
|---|---|---|---|
| 50 | blender_inspect_apariciones.py | (Blender) Inspecciona condenado/karisiri/duende | 2M tris + 8K los 2 primeros; duende 20k sin textura |
| 51 | blender_procesar_apariciones.py | (Blender) Decimate a 15k + texturas 2K + color duende + origen base | 62MB→1MB, 59MB→0.7MB, duende coloreado |
| 52 | ue_importar_apariciones.py | Importa los 3 GLB optimizados | StaticMesh + materiales limpios |
| 53 | ue_inspeccionar_bp_aparicion.py | Inspecciona BP_Apparition e instancias | Billboard Plane + TriggerVolume + M_JW_Apparition |
| 54 | ue_inspeccionar_material_aparicion.py | Params de M_JW_Apparition | Opacity + ApparitionTex (Unlit/Translúcido) |
| 55 | blender_textura_duende.py | (Blender) Textura verde sólida del duende | T_Duende_Green.png |
| 56 | ue_montar_apariciones_3d.py | Cambia Plane por modelo 3D en el BP | Malla cambió pero BP revierte material/escala |
| 57 | ue_enumerar_vars_bp_aparicion.py | Enumera variables del BP | BP no expone variables a Python |
| 58 | ue_colocar_apariciones3d_propias.py | Crea App3D_* propios (mesh+MI+escala) y oculta billboards | 4 apariciones 3D sólidas |
| 59 | ue_material_aparicion3d.py | Crea M_Aparicion3D (Unlit/Translúcido emisivo + Fresnel) + 3 MIs | Fantasmas que brillan de noche |
| 60 | ue_animar_apariciones_sequence.py | LS_Apariciones: materializar/derivar/desvanecer en bucle + auto-play | Apariciones animadas |
| 61 | blender_sintetizar_sonidos.py | (Blender/numpy) Sintetiza 3 sonidos eerie: Karisiri (drone+susurros), Condenado (lamento+cadenas), Duende (piedras+risita) | 3 WAV 44.1kHz loop |
| 62 | ue_colocar_sonidos_apariciones.py | Importa WAV (loop) + AmbientSound espacializado en cada aparición | 4 sonidos colocados, atenuación localizada |
| 63 | ue_reubicar_apariciones_bosque.py | Reubica apariciones AFUERA (bosque/oscuridad) + orienta + mueve sonidos + rehace animación (emergen y se retiran a los árboles) | Karisiri/Condenado/Duende afuera de estructuras |
| 64 | ue_material_fantasma_desaturado.py | M_Aparicion3D_v2 desaturado (fantasma monocromo pálido) + reparenta MIs | Ya no amarillo garish; etéreo |
