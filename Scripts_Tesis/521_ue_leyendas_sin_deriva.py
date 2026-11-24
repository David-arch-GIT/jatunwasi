# 521_ue_leyendas_sin_deriva.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: CAUSA REAL del "las leyendas vuelan": LSA_CriaturasDrift (LS_CriaturasDrift, 1800 frames,
#   auto_play + bucle infinito) anima la transformacion de Cria_Condenado/Duende/Karisiri: las desplaza,
#   sube/baja y gira continuamente (medido en PIE 517: 0.5-4 m/s, z +-25 cm, giros de 180 grados).
#   Se apaga su auto_play (no se borra el actor ni la secuencia). Las leyendas quedan en reposo y solo
#   caminan hacia el visitante cuando las mira (515/516/518). Respaldo del mapa. Guarda.
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/leyendas_521.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_sin_deriva.umap")
    a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "LSA_CriaturasDrift"][0]
    ps = a.get_editor_property("playback_settings")
    res["antes"] = ps.get_editor_property("auto_play")
    ps.set_editor_property("auto_play", False)
    a.set_editor_property("playback_settings", ps)
    a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "LSA_CriaturasDrift"][0]
    res["despues"] = a.get_editor_property("playback_settings").get_editor_property("auto_play")
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
