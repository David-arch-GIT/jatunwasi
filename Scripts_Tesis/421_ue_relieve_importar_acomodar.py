# 421_ue_relieve_importar_acomodar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (1) importar los 42 mosaicos RLV_* de 420 a /Game/JWN/Relieve (sin Nanite, UV de
#   precision completa para que la textura del piso no tiemble, LOD1 al 45 %), material del piso
#   MI_JW_Ground_Earth_V3, colocarlos (tag RELLENO_RELIEVE, sin colision, sin sombra, sin efecto en
#   NavMesh). (2) ACOMODAR sobre el relieve todas las instancias de vegetacion (bosque PCG, relieve
#   PCG, JW_ENV_*, HACFOR_*, HORIZ_*, RELLENO_Campos salvo pircas, RELLENO_Horizonte, luciernagas)
#   sumando la altura del terreno (interpolacion bilineal de relieve_heights.json) -> nada queda
#   enterrado. Guarda en relieve_snap_undo.json los desplazamientos (reversible).
#   Respaldo del .umap antes (solo la primera vez). v2: 1 solo LOD; SKIP_SNAP=True para re-importar.
import unreal, json, os, shutil, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/relieve_ue.json"
SRC = ROOT + r"/Saved/Models/relieve"
DST = "/Game/JWN/Relieve"
SNAP_PREFIX = ("JW_ENV_", "PCG_BosqueVol", "PCG_RelieveVol", "HACFOR_ISM_", "HORIZ_ISM_", "RELLENO_Campos", "RELLENO_Horizonte", "RELLENO_Luciernagas")
res = {"err": None, "steps": []}
try:
    SKIP_SNAP
except NameError:
    SKIP_SNAP = False   # True al re-importar mosaicos: las instancias YA estan acomodadas (alturas identicas)
try:
    if not os.path.exists(ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_relieve_20261124.umap"):
        shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_relieve_20261124.umap")
    rep = json.load(open(SRC + "/report.json"))
    H = json.load(open(ROOT + "/Saved/ClaudeBackups/relieve_heights.json"))
    tasks = []
    for name, cx, cy, nt in rep["tiles"]:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", SRC + "/" + name + ".fbx"); t.set_editor_property("destination_path", DST)
        t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", False)
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    res["steps"].append("import")
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    mi = unreal.load_asset("/Game/JWN/Environment/Materials/MI_JW_Ground_Earth_V3")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("RLV_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    placed = 0; tris = 0
    for name, cx, cy, nt in rep["tiles"]:
        sm = unreal.load_asset(DST + "/" + name)
        if sm is None:
            raise Exception("falta " + name)
        ns = sm.get_editor_property("nanite_settings"); ns.enabled = False; sm.set_editor_property("nanite_settings", ns)
        bs = sms.get_lod_build_settings(sm, 0)
        bs.set_editor_property("use_full_precision_u_vs", True)
        bs.set_editor_property("generate_lightmap_u_vs", False)
        sms.set_lod_build_settings(sm, 0, bs)
        opts = unreal.EditorScriptingMeshReductionOptions()
        opts.set_editor_property("auto_compute_lod_screen_size", False)
        opts.set_editor_property("reduction_settings", [unreal.EditorScriptingMeshReductionSettings(1.0, 1.0)])  # v2: 1 solo LOD (la reduccion abria grietas entre mosaicos)
        sms.set_lods(sm, opts)
        sms.remove_collisions(sm)
        sm.set_material(0, mi)
        unreal.EditorAssetLibrary.save_loaded_asset(sm, False)
        tris += sm.get_num_triangles(0)
        act = unreal.EditorLevelLibrary.spawn_actor_from_object(sm, unreal.Vector(cx, cy, 0))
        act.set_actor_label(name); act.tags = [unreal.Name("RELLENO"), unreal.Name("RELLENO_RELIEVE")]
        c = act.static_mesh_component
        c.set_mobility(unreal.ComponentMobility.STATIC)
        c.set_editor_property("cast_shadow", False)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_editor_property("can_ever_affect_navigation", False)
        c.set_material(0, mi)
        act.set_folder_path("Relieve")
        placed += 1
    res["placed"] = placed; res["tris_lod0"] = tris
    res["steps"].append("placed")

    if SKIP_SNAP:
        raise StopIteration
    X0, Y0, S, NX, NY, HH = H["x0"], H["y0"], H["step"], H["nx"], H["ny"], H["h"]
    def hat(x, y):
        fx = (x - X0) / S; fy = (y - Y0) / S
        i = int(fx // 1); j = int(fy // 1)
        if i < 0 or j < 0 or i >= NX - 1 or j >= NY - 1:
            return 0.0
        tx = fx - i; ty = fy - j
        a = HH[j][i] * (1 - tx) + HH[j][i + 1] * tx
        b = HH[j + 1][i] * (1 - tx) + HH[j + 1][i + 1] * tx
        h = a * (1 - ty) + b * ty
        return h if h > 1.0 else 0.0
    undo = {}; moved = 0; total = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if not lb.startswith(SNAP_PREFIX):
            continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if lb == "RELLENO_Campos" and c.static_mesh and "Fence" in c.static_mesh.get_name():
                continue
            n = c.get_instance_count(); total += n
            key = lb + "|" + c.get_name(); dz = []
            last = -1
            for k in range(n):
                t = c.get_instance_transform(k, True)
                h = hat(t.translation.x, t.translation.y)
                dz.append(round(h, 1))
                if h > 0:
                    last = k
            for k in range(n):
                if dz[k] > 0:
                    t = c.get_instance_transform(k, True)
                    t.translation = unreal.Vector(t.translation.x, t.translation.y, t.translation.z + dz[k])
                    c.update_instance_transform(k, t, True, k == last, True)
                    moved += 1
            undo[key] = dz
    json.dump(undo, open(ROOT + "/Saved/ClaudeBackups/relieve_snap_undo.json", "w"))
    res["instances_total"] = total; res["instances_moved"] = moved
    res["steps"].append("snapped")
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(300, 2400, 260), unreal.Rotator(0, -6, 35))
except StopIteration:
    res["steps"].append("snap_skipped")
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
