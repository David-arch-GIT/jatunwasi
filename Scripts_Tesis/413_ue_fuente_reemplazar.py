# 413_ue_fuente_reemplazar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: importar SM_Fuente_Plaza_Q (salida del gate 412: 40k tris, escala real 5.27 m, origen en
#   la base) a /Game/JWN/Plaza/Fuente, SIN Nanite (Quest no lo usa), 4 LODs (100/50/25/10 %),
#   colision por descomposicion convexa, y ponerla en el actor PLZ_FuenteMejorada con escala
#   UNIFORME 1 (antes 5.375 x 6 x 6.97 = deformada). Mantiene el mismo material (MIvd_fuente) y las
#   mismas banderas de navegacion/colision del actor. Respaldo del .umap antes.
import unreal, json, shutil, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/fuente_reemplazo.json"
FBX = ROOT + r"/Saved/Models/plaza/SM_Fuente_Plaza_Q.fbx"
DST = "/Game/JWN/Plaza/Fuente"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap",
                 ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_fuente_20261124.umap")
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", FBX); t.set_editor_property("destination_path", DST)
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", False)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    sm = unreal.load_asset(DST + "/SM_Fuente_Plaza_Q")
    if sm is None:
        raise Exception("import fallo: " + str(t.get_editor_property("imported_object_paths")))
    ns = sm.get_editor_property("nanite_settings"); ns.enabled = False; sm.set_editor_property("nanite_settings", ns)
    opts = unreal.EditorScriptingMeshReductionOptions()
    opts.set_editor_property("auto_compute_lod_screen_size", False)
    opts.set_editor_property("reduction_settings", [
        unreal.EditorScriptingMeshReductionSettings(1.0, 1.0),
        unreal.EditorScriptingMeshReductionSettings(0.5, 0.45),
        unreal.EditorScriptingMeshReductionSettings(0.25, 0.22),
        unreal.EditorScriptingMeshReductionSettings(0.10, 0.10)])
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    sms.set_lods(sm, opts)
    sms.remove_collisions(sm)
    sms.set_convex_decomposition_collisions(sm, 12, 16, 150000)
    mi = unreal.load_asset("/Game/JWN/TripoClean2/MIvd_fuente")
    sm.set_material(0, mi)
    unreal.EditorAssetLibrary.save_loaded_asset(sm, False)
    res["lods"] = [sm.get_num_triangles(l) for l in range(sm.get_num_lods())]
    b = sm.get_bounding_box(); res["size_cm"] = [round(b.max.x - b.min.x), round(b.max.y - b.min.y), round(b.max.z - b.min.z)]
    a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "PLZ_FuenteMejorada"][0]
    c = a.get_component_by_class(unreal.StaticMeshComponent)
    res["old"] = {"mesh": c.static_mesh.get_path_name(), "scale": [a.get_actor_scale3d().x, a.get_actor_scale3d().y, a.get_actor_scale3d().z],
                  "nav": c.get_editor_property("can_ever_affect_navigation"), "coll": str(c.get_collision_enabled()),
                  "shadow": c.get_editor_property("cast_shadow")}
    c.set_static_mesh(sm)
    c.set_material(0, mi)
    a.set_actor_scale3d(unreal.Vector(1, 1, 1))
    a.set_actor_location(unreal.Vector(0, -1000, 0), False, False)
    c.set_editor_property("cast_shadow", False)
    res["new_size_world"] = str(a.get_actor_bounds(False)[1])
    pl = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "PLZBF_CentralFountain"][0]
    pc = pl.get_component_by_class(unreal.StaticMeshComponent)
    res["plzbf"] = {"hidden_game": pl.get_editor_property("hidden"), "visible": pc.get_editor_property("visible"), "hig": pc.get_editor_property("hidden_in_game")}
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-750, -1000, 330), unreal.Rotator(0, -8, 0))
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
