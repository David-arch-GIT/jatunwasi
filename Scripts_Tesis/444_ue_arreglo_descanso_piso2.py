# 444_ue_arreglo_descanso_piso2.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: ARREGLAR la subida al 2do piso de la hacienda (la usuaria: "la escalera funciono pero la
#   entrada no me dejo pasar"). Diagnostico 443: el NavMesh de la rampa se corta en el ultimo tramo
#   (z 345-410) porque 3 cajas de colision de un parche anterior (COL_Hac_EscBridge, COL_Hac_Desc2P,
#   COL_Hac_Desc2P_B) quedaron con PITCH 12 (inclinadas) en vez de YAW 12.1 (giro del edificio) ->
#   techo bajo sobre la rampa + descanso torcido.
#   Arreglo: esas 3 cajas -> sin colision (no se borran; reversible) y se coloca COL_Hac_Descanso2P:
#   losa plana invisible yaw 12.1, superficie a z=430 (= corredor 432 / salon 426), que empieza donde
#   la rampa llega a ~414 (y=-2245) y cubre el descanso hasta el corredor. Respaldo del .umap.
import unreal, json, shutil, os, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/descanso2p.json"
res = {"err": None}
try:
    if not os.path.exists(ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_piso2_20261124.umap"):
        shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_piso2_20261124.umap")
    prev = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if lb in ("COL_Hac_EscBridge", "COL_Hac_Desc2P", "COL_Hac_Desc2P_B"):
            c = a.get_component_by_class(unreal.StaticMeshComponent)
            prev[lb] = str(c.get_collision_enabled())
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            c.set_editor_property("can_ever_affect_navigation", False)
        if lb == "COL_Hac_Descanso2P":
            unreal.EditorLevelLibrary.destroy_actor(a)
    res["prev_collision"] = prev
    cube = unreal.load_asset("/Engine/BasicShapes/Cube")
    # losa: 420 x 520 cm, 10 cm de grosor, superficie z=430; centro desplazado hacia el corredor
    a = unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(-7478, -1990, 425), unreal.Rotator(0, 0, 12.1))
    a.set_actor_label("COL_Hac_Descanso2P")
    a.set_actor_scale3d(unreal.Vector(4.2, 5.2, 0.1))
    c = a.static_mesh_component
    c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    c.set_collision_profile_name("BlockAll")
    c.set_editor_property("can_ever_affect_navigation", True)
    c.set_editor_property("cast_shadow", False)
    a.set_actor_hidden_in_game(True)
    c.set_editor_property("visible", False)
    o, e = a.get_actor_bounds(False)
    res["losa_bounds"] = [round(o.x - e.x), round(o.y - e.y), round(o.z - e.z), round(o.x + e.x), round(o.y + e.y), round(o.z + e.z)]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
