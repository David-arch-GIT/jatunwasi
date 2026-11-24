# 437_ue_muestrario_kit_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: MUESTRARIO temporal para evaluar la calidad visual del kit /Game/JWN/Props/Convento
#   (35 piezas sin usar) antes de amoblar el convento. PHASE="poner": coloca cada pieza en fila
#   (label TMPKIT_*) en un campo vacio al sur (y=-9000) + datos de tris/tamano. PHASE="quitar": borra
#   los TMPKIT_* (actores temporales creados aqui, no assets).
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "poner"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/kit_muestrario.json"
res = {"err": None, "items": []}
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("TMPKIT_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    if PHASE == "poner":
        reg = unreal.AssetRegistryHelpers.get_asset_registry()
        meshes = sorted(str(ad.package_name) for ad in reg.get_assets_by_path("/Game/JWN/Props/Convento", recursive=False) if str(ad.asset_class_path.asset_name) == "StaticMesh")
        x = 0.0
        for i, p in enumerate(meshes):
            sm = unreal.load_asset(p); b = sm.get_bounding_box(); w = b.max.x - b.min.x
            row = i // 9; col_x = x if row == 0 else None
            a = unreal.EditorLevelLibrary.spawn_actor_from_object(sm, unreal.Vector(0, 0, 0))
            a.set_actor_label("TMPKIT_%02d_%s" % (i, p.split("/")[-1].replace("KitConvento_SM_", "")))
            res["items"].append([i, p.split("/")[-1], sm.get_num_triangles(0), [round(b.max.x - b.min.x), round(b.max.y - b.min.y), round(b.max.z - b.min.z)],
                                 [m.material_interface.get_name() if m.material_interface else None for m in sm.static_materials][:3]])
        # distribuir en grilla 9 x n con separacion segun tamano
        acts = sorted([a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith("TMPKIT_")], key=lambda a: a.get_actor_label())
        for i, a in enumerate(acts):
            r, c = i // 9, i % 9
            a.set_actor_location(unreal.Vector(-1600 + c * 400, -9000 - r * 450, 0), False, False)
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
