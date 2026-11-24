# 448_ue_final_recursos.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: RECURSOS del FINAL del recorrido en la Sala de Baile (2do piso hacienda), elegido por el
#   usuario: vals que sube, faroles uno a uno, luces que caen, Adela aparece y se despide (Convai
#   disponible), fundido a negro y creditos (pantalla negra y fin).
#   - importa A_Adela_Despedida (misma concurrencia que los relatos, prioridad alta) y T_CreditosFinales
#   - MPC_Final (TF faroles, TL luces, T0 fundido; por defecto 1e6 = apagado)
#   - M_FarolLuz (unlit aditivo; se enciende en orden por PerInstanceCustomData 0 a partir de TF)
#   - M_LucesCaen (unlit aditivo; WPO de caida en bucle + vaiven; aparece desde TL)
#   - M_FadeFinal (negro translucido sin depth test; opacidad sube 3 s desde T0)
#   - M_CreditosFinal (textura de creditos, sin depth test)
#   - FINAL_Faroles (8 faroles Megascans) + FINAL_FarolLuz (ISM con indice) + FINAL_LucesCaen (70 luces)
#   - BP_XRPawn: componentes FadeFinal (esfera en la camara) y CreditosFinal (plano a 1.2 m), ocultos
#   - tags: AMB_SalaBaile "ValsSalon", Adela_Convai "AdelaGuia"
#   Respaldo .umap y BP_XRPawn.
import unreal, json, math, shutil, os, random, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/final_recursos.json"
FX = "/Game/JWN/FX"; UI = "/Game/JWN/UI"
res = {"err": None, "steps": []}
def ci(n):
    c = unreal.CustomInput(); c.set_editor_property("input_name", n); return c
try:
    bk = ROOT + "/Saved/ClaudeBackups/"
    if not os.path.exists(bk + "MAP_CLEAN_pre_final_20261124.umap"):
        shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", bk + "MAP_CLEAN_pre_final_20261124.umap")
        shutil.copy2(ROOT + "/Content/XRFramework/Blueprints/BP_XRPawn.uasset", bk + "BP_XRPawn_pre_final.uasset")
        shutil.copy2(ROOT + "/Content/JWN/Blueprints/BP_GestorRecorrido.uasset", bk + "BP_GestorRecorrido_pre_final.uasset")
    at = unreal.AssetToolsHelpers.get_asset_tools(); mel = unreal.MaterialEditingLibrary
    def imp(src, dst, name=None):
        t = unreal.AssetImportTask(); t.set_editor_property("filename", src); t.set_editor_property("destination_path", dst)
        if name: t.set_editor_property("destination_name", name)
        t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
        at.import_asset_tasks([t])
    imp(ROOT + "/Saved/NarrWav/A_Adela_Despedida.wav", "/Game/JWN/Audio/Relatos")
    ref = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Relato_convento"); voz = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Adela_Despedida")
    for p in ("concurrency_set", "sound_class_object", "attenuation_settings"):
        voz.set_editor_property(p, ref.get_editor_property(p))
    voz.set_editor_property("priority", max(4.0, ref.get_editor_property("priority") + 1.0))
    unreal.EditorAssetLibrary.save_loaded_asset(voz, False)
    imp(ROOT + "/Saved/ClaudeBackups/creditos_finales.png", UI, "T_CreditosFinales")
    tex = unreal.load_asset(UI + "/T_CreditosFinales")
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("never_stream", True); tex.set_editor_property("srgb", True)
    unreal.EditorAssetLibrary.save_loaded_asset(tex, False)
    res["steps"].append("audio+tex")
    # ---- MPC ----
    mp = FX + "/MPC_Final"
    mpc = unreal.load_asset(mp) if unreal.EditorAssetLibrary.does_asset_exist(mp) else at.create_asset("MPC_Final", FX, unreal.MaterialParameterCollection, unreal.MaterialParameterCollectionFactoryNew())
    sc = []
    for n in ("TF", "TL", "T0"):
        p = unreal.CollectionScalarParameter(); p.set_editor_property("parameter_name", n); p.set_editor_property("default_value", 1000000.0); sc.append(p)
    mpc.set_editor_property("scalar_parameters", sc)
    unreal.EditorAssetLibrary.save_loaded_asset(mpc, False)
    def newmat(name):
        p = FX + "/" + name
        m = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset(name, FX, unreal.Material, unreal.MaterialFactoryNew())
        mel.delete_all_material_expressions(m); m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        return m
    def coll(m, pname, x, y):
        e = mel.create_material_expression(m, unreal.MaterialExpressionCollectionParameter, x, y)
        e.set_editor_property("collection", mpc); e.set_editor_property("parameter_name", pname); return e
    # M_FarolLuz
    m = newmat("M_FarolLuz"); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE); m.set_editor_property("used_with_instanced_static_meshes", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 0); tf = coll(m, "TF", -900, 150)
    idx = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceCustomData, -900, 300); idx.set_editor_property("data_index", 0)
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -900, 450); fr.set_editor_property("exponent", 1.5)
    cu = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 150); cu.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    cu.set_editor_property("code", "float on = saturate((T - TF - I * 0.8) / 0.6); float fl = 0.9 + 0.1 * sin(T * 9.0 + I * 2.3); return float3(1.0, 0.62, 0.22) * 2.2 * on * fl * (1.0 - F);")
    cu.set_editor_property("inputs", [ci("T"), ci("TF"), ci("I"), ci("F")])
    mel.connect_material_expressions(t, "", cu, "T"); mel.connect_material_expressions(tf, "", cu, "TF"); mel.connect_material_expressions(idx, "", cu, "I"); mel.connect_material_expressions(fr, "", cu, "F")
    mel.connect_material_property(cu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); mel.recompile_material(m); unreal.EditorAssetLibrary.save_asset(FX + "/M_FarolLuz", False)
    m_farol = m
    # M_LucesCaen
    m = newmat("M_LucesCaen"); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE); m.set_editor_property("used_with_instanced_static_meshes", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 0); tl = coll(m, "TL", -900, 150)
    r = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -900, 300)
    w = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 300); w.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    w.set_editor_property("code", "float f = frac(T * (0.05 + R * 0.04) + R * 7.0); return float3(sin(T * 0.7 + R * 40.0) * 25.0, cos(T * 0.6 + R * 30.0) * 25.0, -f * 260.0);")
    w.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", w, "T"); mel.connect_material_expressions(r, "", w, "R")
    mel.connect_material_property(w, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    e = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 0); e.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    e.set_editor_property("code", "float f = frac(T * (0.05 + R * 0.04) + R * 7.0); float on = saturate((T - TL) / 2.5); float tw = 0.6 + 0.4 * sin(T * (3.0 + R * 4.0) + R * 20.0); return float3(1.0, 0.78, 0.35) * 1.8 * on * sin(3.14159 * f) * tw;")
    e.set_editor_property("inputs", [ci("T"), ci("R"), ci("TL")])
    mel.connect_material_expressions(t, "", e, "T"); mel.connect_material_expressions(r, "", e, "R"); mel.connect_material_expressions(tl, "", e, "TL")
    mel.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); mel.recompile_material(m); unreal.EditorAssetLibrary.save_asset(FX + "/M_LucesCaen", False)
    m_luces = m
    # M_FadeFinal
    m = newmat("M_FadeFinal"); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("two_sided", True)
    m.set_editor_property("disable_depth_test", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -700, 0); t0 = coll(m, "T0", -700, 150)
    o = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -400, 100); o.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    o.set_editor_property("code", "return saturate((T - T0) / 3.0);"); o.set_editor_property("inputs", [ci("T"), ci("T0")])
    mel.connect_material_expressions(t, "", o, "T"); mel.connect_material_expressions(t0, "", o, "T0")
    mel.connect_material_property(o, "", unreal.MaterialProperty.MP_OPACITY)
    k = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, -100); k.set_editor_property("constant", unreal.LinearColor(0, 0, 0, 1))
    mel.connect_material_property(k, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR); mel.recompile_material(m); unreal.EditorAssetLibrary.save_asset(FX + "/M_FadeFinal", False)
    m_fade = m
    # M_CreditosFinal
    m = newmat("M_CreditosFinal"); m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT); m.set_editor_property("disable_depth_test", True)
    ts = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -500, 0); ts.set_editor_property("texture", tex)
    ts.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
    mel.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    one = mel.create_material_expression(m, unreal.MaterialExpressionConstant, -500, 200); one.set_editor_property("r", 1.0)
    mel.connect_material_property(one, "", unreal.MaterialProperty.MP_OPACITY); mel.recompile_material(m); unreal.EditorAssetLibrary.save_asset(FX + "/M_CreditosFinal", False)
    m_cred = m
    res["steps"].append("materiales")
    # ---- actores del salon ----
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("FINAL_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    def nav_ok(x, y):
        r2 = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 432), None, None, unreal.Vector(10, 10, 30))
        p = r2[0] if isinstance(r2, tuple) else r2
        if p is None: return None
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x + dx * 35, y + dy * 35, 500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            if h and h.to_tuple()[0]: return None
        return p.z
    CX, CY = -8375, -1600
    cands = [(-8700, -1300), (-8375, -1300), (-8050, -1300), (-8820, -1600), (-8700, -1900), (-8375, -1900), (-7930, -1450), (-8820, -1420)]
    spots = []
    for x, y in cands:
        z = None; xx, yy = x, y
        for k in range(8):
            z = nav_ok(xx, yy)
            if z is not None: break
            xx += (CX - x) * 0.08; yy += (CY - y) * 0.08
        if z is not None: spots.append((xx, yy, z))
    res["faroles"] = [[round(a), round(b), round(c)] for a, b, c in spots]
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
    def ism_actor(label, mesh, mat, inst, custom=False, cull=4000):
        act = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
        act.set_actor_label(label); act.tags = [unreal.Name("RELLENO"), unreal.Name("FINAL")]; act.set_folder_path("Final_Recorrido")
        root = sds.k2_gather_subobject_data_for_instance(act)[0]
        hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.InstancedStaticMeshComponent, blueprint_context=None))
        c = lib.get_object(lib.get_data(hh)); c.set_static_mesh(unreal.load_asset(mesh))
        if mat:
            for i in range(c.get_num_materials()): c.set_material(i, mat)
        c.set_mobility(unreal.ComponentMobility.STATIC); c.set_editor_property("cast_shadow", False)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); c.set_editor_property("can_ever_affect_navigation", False)
        c.set_editor_property("instance_end_cull_distance", cull)
        if custom: c.set_editor_property("num_custom_data_floats", 1)
        c.add_instances(inst, False, True)
        if custom:
            for i in range(len(inst)): c.set_custom_data_value(i, 0, float(i), i == len(inst) - 1)
        return c
    lant = "/Game/Megascans/3D_Assets/Traditional_Lantern_xccpecydw/S_Traditional_Lantern_xccpecydw_lod3"
    ism_actor("FINAL_Faroles", lant, None, [unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, random.uniform(0, 360)), unreal.Vector(0.55, 0.55, 0.55)) for x, y, z in spots], cull=3000)
    ism_actor("FINAL_FarolLuz", "/Engine/BasicShapes/Sphere", m_farol, [unreal.Transform(unreal.Vector(x, y, z + 36), unreal.Rotator(0, 0, 0), unreal.Vector(0.16, 0.16, 0.2)) for x, y, z in spots], custom=True, cull=3000)
    random.seed(448)
    luces = [unreal.Transform(unreal.Vector(random.uniform(-8800, -7950), random.uniform(-1900, -1300), random.uniform(700, 760)), unreal.Rotator(0, 0, 0), unreal.Vector(0.035, 0.035, 0.035)) for _ in range(70)]
    cl = ism_actor("FINAL_LucesCaen", "/Engine/BasicShapes/Sphere", m_luces, luces, cull=3000)
    cl.set_editor_property("bounds_scale", 4.0)
    res["steps"].append("actores")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if lb == "AMB_SalaBaile" and unreal.Name("ValsSalon") not in a.tags: a.tags = list(a.tags) + [unreal.Name("ValsSalon")]
        if lb == "Adela_Convai" and unreal.Name("AdelaGuia") not in a.tags: a.tags = list(a.tags) + [unreal.Name("AdelaGuia")]
    # ---- componentes del pawn ----
    bp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    byname = {str(lib.get_variable_name(lib.get_data(h))): h for h in hs}
    cam = byname["Camera"]
    def add_comp(name, mesh, mat, loc, rot, scale, prio):
        if name in byname:
            c = lib.get_object(lib.get_data(byname[name]))
        else:
            hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=cam, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
            sds.rename_subobject(hh, unreal.Text(name)); c = lib.get_object(lib.get_data(hh))
        c.set_static_mesh(unreal.load_asset(mesh)); c.set_material(0, mat)
        c.set_editor_property("relative_location", loc); c.set_editor_property("relative_rotation", rot); c.set_editor_property("relative_scale3d", scale)
        c.set_editor_property("visible", False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_editor_property("cast_shadow", False); c.set_editor_property("can_ever_affect_navigation", False)
        c.set_editor_property("translucency_sort_priority", prio)
    add_comp("FadeFinal", "/Engine/BasicShapes/Sphere", m_fade, unreal.Vector(0, 0, 0), unreal.Rotator(0, 0, 0), unreal.Vector(0.6, 0.6, 0.6), 10)
    add_comp("CreditosFinal", "/Engine/BasicShapes/Plane", m_cred, unreal.Vector(120, 0, 0), unreal.Rotator(90, 0, 90), unreal.Vector(0.9, 1.6, 1.0), 20)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp); unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    res["steps"].append("pawn")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    res["steps"].append("guardado")
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
