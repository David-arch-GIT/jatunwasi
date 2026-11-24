# 427_ue_puertas_importar_colocar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: llevar las puertas del gate 426 al mapa:
#   1) respaldo .umap + BP_PuertaProximidad
#   2) importa texturas base (templo 2048, convento/hacienda 1024) y crea MI_Puerta_* hijos de
#      M_GlowVeryDim (mismo look nocturno que la fuente y props Tripo)
#   3) importa las 9 piezas (/Game/JWN/Puertas): sin Nanite, 3 LODs, hojas con colision de caja,
#      marco/montante sin colision
#   4) agrega componente "Marco" (fijo) a BP_PuertaProximidad
#   5) coloca PUERTA_Templo, PUERTA_Hacienda, PUERTA_Convento_A/B en los vanos medidos (424/425),
#      bisagras en su sitio, giro hacia el interior; oculta TMP_Portal (arco viejo, sin borrar)
#   Reporta bounds de una pieza para confirmar el cambio de eje Y Blender->UE.
import unreal, json, os, shutil, math, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/puertas_ue.json"
SRC = ROOT + r"/Saved/Models/puertas/"
DST = "/Game/JWN/Puertas"
BP = "/Game/JWN/Blueprints/BP_PuertaProximidad"
res = {"err": None, "steps": []}
try:
    bk = ROOT + "/Saved/ClaudeBackups/"
    if not os.path.exists(bk + "MAP_CLEAN_pre_puertas_20261124.umap"):
        shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", bk + "MAP_CLEAN_pre_puertas_20261124.umap")
        shutil.copy2(ROOT + "/Content/JWN/Blueprints/BP_PuertaProximidad.uasset", bk + "BP_PuertaProximidad_pre_puertas.uasset")
    rep = json.load(open(SRC + "report.json"))
    at = unreal.AssetToolsHelpers.get_asset_tools()
    tasks = []
    files = [f for f in os.listdir(SRC) if (f.startswith("T_Puerta_") or f.startswith("SM_Puerta")) and f.split(".")[-1] in ("jpg", "png", "fbx")]
    for f in files:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", SRC + f); t.set_editor_property("destination_path", DST)
        t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", False)
        tasks.append(t)
    at.import_asset_tasks(tasks)
    res["steps"].append("import %d" % len(tasks))
    parent = unreal.load_asset("/Game/JWN/Convento/M_GlowVeryDim")
    mis = {}
    for door, size in (("Templo", 2048), ("Convento", 1024), ("Hacienda", 1024)):
        tex = unreal.load_asset(DST + "/T_Puerta_%s_BC" % door)
        tex.set_editor_property("max_texture_size", size)
        unreal.EditorAssetLibrary.save_loaded_asset(tex, False)
        p = DST + "/MI_Puerta_" + door
        mi = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset("MI_Puerta_" + door, DST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mi.set_editor_property("parent", parent)
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi, "BaseColor", tex)
        unreal.EditorAssetLibrary.save_loaded_asset(mi, False)
        mis[door] = mi
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    meshes = {}
    for f in files:
        if not f.endswith(".fbx"): continue
        nm = f[:-4]; sm = unreal.load_asset(DST + "/" + nm)
        ns = sm.get_editor_property("nanite_settings"); ns.enabled = False; sm.set_editor_property("nanite_settings", ns)
        o = unreal.EditorScriptingMeshReductionOptions(); o.set_editor_property("auto_compute_lod_screen_size", False)
        o.set_editor_property("reduction_settings", [unreal.EditorScriptingMeshReductionSettings(1.0, 1.0),
                                                     unreal.EditorScriptingMeshReductionSettings(0.5, 0.35),
                                                     unreal.EditorScriptingMeshReductionSettings(0.25, 0.15)])
        sms.set_lods(sm, o)
        sms.remove_collisions(sm)
        if "_Hoja" in nm:
            sms.add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
        door = nm.split("_")[1].replace("Puerta", "")
        sm.set_material(0, mis[door])
        unreal.EditorAssetLibrary.save_loaded_asset(sm, False)
        b = sm.get_bounding_box()
        meshes[nm] = sm
        res[nm] = {"lods": [sm.get_num_triangles(l) for l in range(sm.get_num_lods())],
                   "min": [round(b.min.x, 1), round(b.min.y, 1), round(b.min.z, 1)], "max": [round(b.max.x, 1), round(b.max.y, 1), round(b.max.z, 1)]}
    res["steps"].append("meshes")
    # eje Y: en Blender el marco del templo ocupa y[-0.252,-0.036] m -> si en UE da positivo, Y se invirtio
    mb = res["SM_PuertaTemplo_Marco"]
    YF = -1.0 if mb["max"][1] > 0 else 1.0
    res["y_flip"] = YF
    # componente Marco en el BP
    bp = unreal.load_asset(BP)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    names = [str(lib.get_variable_name(lib.get_data(h))) for h in hs]
    if "Marco" not in names:
        hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=hs[0], new_class=unreal.StaticMeshComponent, blueprint_context=bp))
        sds.rename_subobject(hh, unreal.Text("Marco"))
        c = lib.get_object(lib.get_data(hh))
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_editor_property("can_ever_affect_navigation", False)
        c.set_editor_property("cast_shadow", False)
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    res["steps"].append("bp_marco")
    # colocar
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("PUERTA_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
        if a.get_actor_label() == "TMP_Portal":
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_visibility(False)
            a.set_actor_hidden_in_game(True)
    def floor_at(x, y, z0):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, z0 + 120), unreal.Vector(x, y, z0 - 150), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        return t[4].z if (t and t[0]) else z0
    cls = unreal.EditorAssetLibrary.load_blueprint_class(BP)
    T, H, C = rep["templo"], rep["hacienda"], rep["convento"]
    DOORS = [
        ("PUERTA_Templo", (50.0, 10340.0, 10.0), 180.0, "SM_PuertaTemplo_Marco", "SM_PuertaTemplo_HojaIzq", "SM_PuertaTemplo_HojaDer", T["hinge_x"], T["pivot_y"]),
        ("PUERTA_Hacienda", (-7317.2, -1019.6, 60.0), 10.3, "SM_PuertaHacienda_Marco", "SM_PuertaHacienda_HojaIzq", "SM_PuertaHacienda_HojaDer", H["hinge_x"], H["pivot_y"]),
        ("PUERTA_Convento_A", (6097.4, 3720.0, 0.0), 180.0, "SM_PuertaConvento_Montante", None, "SM_PuertaConvento_HojaDer", C["hinge_x"], C["pivot_y"]),
        ("PUERTA_Convento_B", (6497.4, 3720.0, 0.0), 180.0, "SM_PuertaConvento_Montante", "SM_PuertaConvento_HojaIzq", None, C["hinge_x"], C["pivot_y"]),
    ]
    placed = []
    for lb, (x, y, z), yaw, mk, hl, hr, hx, py in DOORS:
        fz = floor_at(x, y + (60 if yaw == 180 else 0), z)
        a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, unreal.Vector(x, y, fz), unreal.Rotator(0, 0, yaw))
        a.set_actor_label(lb); a.set_folder_path("Puertas")
        comps = {c.get_name(): c for c in a.get_components_by_class(unreal.StaticMeshComponent)}
        def comp(prefix):
            return [c for n, c in comps.items() if n.startswith(prefix)][0]
        m = comp("Marco"); m.set_static_mesh(meshes[mk])
        m.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); m.set_editor_property("can_ever_affect_navigation", False)
        for pre, mesh, sx in (("HojaIzq", hl, -1), ("HojaDer", hr, 1)):
            c = comp(pre)
            c.set_editor_property("relative_location", unreal.Vector(sx * hx * 100.0, YF * py * 100.0, 0.0))
            c.set_static_mesh(meshes[mesh] if mesh else None)
            if not mesh:
                c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        placed.append([lb, round(x), round(y), round(fz, 1), yaw])
    res["placed"] = placed
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    res["steps"].append("placed_saved")
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
