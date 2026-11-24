# 502_ue_inicio_mirando_adela.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (1) descripciones UNICAS para IA_JW_Mover/BotonA/Gatillo (OpenXR exige nombres localizados
#   distintos). (2) pedido de la usuaria: el visitante debe APARECER MIRANDO DE FRENTE a Adela y al cartel
#   de controles. Se orienta PlayerStart_Inicio hacia el punto medio entre Adela_Convai y GUIA_Controles.
#   Respaldo del mapa. Guarda.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inicio_mirando.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    for n, d in (("IA_JW_Mover", "JW Mover palanca derecha"), ("IA_JW_BotonA", "JW Boton A sonido ambiente"), ("IA_JW_Gatillo", "JW Gatillo derecho moneda")):
        ia = unreal.load_asset("/Game/JWN/Input/" + n)
        ia.set_editor_property("action_description", unreal.Text(d))
        res[n] = unreal.EditorAssetLibrary.save_loaded_asset(ia, False)
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_inicio_mirando.umap")
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    ps = acts["PlayerStart_Inicio"]; P = ps.get_actor_location()
    A = acts["Adela_Convai"].get_actor_location()
    G = acts["GUIA_Controles"].get_actor_location() if "GUIA_Controles" in acts else A
    res["posiciones"] = {"inicio": [round(P.x), round(P.y), round(P.z)], "adela": [round(A.x), round(A.y), round(A.z)], "cartel": [round(G.x), round(G.y), round(G.z)]}
    yaw_a = math.degrees(math.atan2(A.y - P.y, A.x - P.x)); yaw_g = math.degrees(math.atan2(G.y - P.y, G.x - P.x))
    M = ((A.x + G.x) / 2, (A.y + G.y) / 2)
    yaw = math.degrees(math.atan2(M[1] - P.y, M[0] - P.x))
    res["yaw_antes"] = round(ps.get_actor_rotation().yaw, 1)
    ps.set_actor_rotation(unreal.Rotator(0, 0, yaw), False)
    res["yaw_nuevo"] = round(ps.get_actor_rotation().yaw, 1)
    res["angulo_a_adela"] = round(yaw_a - yaw, 1); res["angulo_al_cartel"] = round(yaw_g - yaw, 1)
    res["dist_adela_m"] = round(math.hypot(A.x - P.x, A.y - P.y) / 100, 2); res["dist_cartel_m"] = round(math.hypot(G.x - P.x, G.y - P.y) / 100, 2)
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
