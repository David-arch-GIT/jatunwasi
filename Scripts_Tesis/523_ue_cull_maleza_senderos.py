# 523_ue_cull_maleza_senderos.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: fluidez en los senderos (visor 24-nov: 33-52 FPS fuera de la plaza, GPU 97 %, limitado por
#   fragmentos/sobredibujado) SIN perder calidad visible. Auditoria 522: ~1.900 arbustos/helechos/hierbas
#   ENMASCARADOS de senderos (HACFOR_ISM, JW_ENV_Shrubs, PATHUS_ISM, CONV_ISM) se dibujaban hasta 90 m,
#   mientras el bosque principal (PCG_BosqueVol) ya corta a 28-35 m. De noche con niebla (densidad 0.03,
#   inicio 15 m) la maleza a mas de 35 m no se distingue. Se igualan a 2800/3500 cm (desvanecido suave).
#   Solo maleza (no arboles, no estructuras). Antes/despues con capturas desde 3 senderos. Respaldo del mapa.
import unreal, json, traceback, shutil, re
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_523.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
ACTORES = re.compile(r"^(HACFOR_ISM|JW_ENV_Shrubs|JW_ENV_Grass|PATHUS_ISM|CONV_ISM)")
MALLAS = re.compile(r"(Fern|ForestBush|ForestPlant|Mossy_Grass|Clover|GrassForest)")
res = {"err": None, "cambiados": []}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_cull_maleza.umap")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if not ACTORES.match(a.get_actor_label()): continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if not c.static_mesh or not MALLAS.search(c.static_mesh.get_name()): continue
            fin = c.get_editor_property("instance_end_cull_distance")
            if fin == 0 or fin > 3500:
                c.set_editor_property("instance_start_cull_distance", 2800)
                c.set_editor_property("instance_end_cull_distance", 3500)
                res["cambiados"].append([a.get_actor_label(), c.static_mesh.get_name(), c.get_instance_count(), fin])
    res["n"] = len(res["cambiados"]); res["inst"] = sum(x[2] for x in res["cambiados"])
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
