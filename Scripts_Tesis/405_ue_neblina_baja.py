# 405_ue_neblina_baja.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: neblina baja que se arrastra junto a las 3 leyendas. Planos horizontales (HISM, Plane)
#   a 15-45 cm del suelo con material translucido unlit: dos capas de ruido suave desplazandose a
#   distinta velocidad (PerInstanceRandom desfasa cada plano), bordes radiales difuminados y
#   desvanecido cuando la camara esta cerca/dentro (nunca tapa la vista). Barato, sin luces.
#   Actor RELLENO_Neblina (tag RELLENO).
import unreal, json, math, random, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/neblina.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"err": None}
MAT = "/Game/JWN/FX/M_NeblinaBaja"
NOISE = "/Engine/MapTemplates/TilingNoise05"
LEG = {"karisiri": ((3881, 3281), (4000, 1700)), "condenado": ((1031, 8380), (325, 7596)), "duende": ((-4135, 731), (-4310, -143))}
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        m = unreal.load_asset(MAT); mel.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_NeblinaBaja", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    tex = unreal.load_asset(NOISE)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1300, 0)
    r = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -1300, 120)
    uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1300, 240)
    uvs = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -1000, 100)
    uvs.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT2)
    uvs.set_editor_property("code", "return UV * 1.3 + float2(T * 0.010 + R * 7.0, T * 0.004 + R * 3.0);")
    uvs.set_editor_property("inputs", [ci("UV"), ci("T"), ci("R")])
    mel.connect_material_expressions(uv, "", uvs, "UV"); mel.connect_material_expressions(t, "", uvs, "T"); mel.connect_material_expressions(r, "", uvs, "R")
    uvs2 = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -1000, 300)
    uvs2.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT2)
    uvs2.set_editor_property("code", "return UV * 2.7 + float2(-T * 0.017 + R * 11.0, T * 0.009 + R * 5.0);")
    uvs2.set_editor_property("inputs", [ci("UV"), ci("T"), ci("R")])
    mel.connect_material_expressions(uv, "", uvs2, "UV"); mel.connect_material_expressions(t, "", uvs2, "T"); mel.connect_material_expressions(r, "", uvs2, "R")
    n1 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -750, 100); n1.set_editor_property("texture", tex)
    n2 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -750, 300); n2.set_editor_property("texture", tex)
    mel.connect_material_expressions(uvs, "", n1, "UVs"); mel.connect_material_expressions(uvs2, "", n2, "UVs")
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -1000, 500)
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 600)
    op = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -450, 250)
    op.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    op.set_editor_property("code",
        "float d = distance(UV, float2(0.5, 0.5)) * 2.0;"
        "float edge = pow(saturate(1.0 - d), 1.6);"
        "float n = saturate(A * 1.2 * (0.55 + B * 0.9) - 0.15);"
        "float cf = saturate((distance(C, W) - 120.0) / 280.0);"
        "return n * edge * cf * 0.55;")
    op.set_editor_property("inputs", [ci("UV"), ci("A"), ci("B"), ci("C"), ci("W")])
    mel.connect_material_expressions(uv, "", op, "UV"); mel.connect_material_expressions(n1, "R", op, "A"); mel.connect_material_expressions(n2, "R", op, "B")
    mel.connect_material_expressions(cam, "", op, "C"); mel.connect_material_expressions(wp, "", op, "W")
    mel.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -450, -50)
    col.set_editor_property("constant", unreal.LinearColor(0.32, 0.36, 0.45, 1.0))
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)

    def gz(x, y):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return None
        tp = h.to_tuple(); return tp[4].z if tp[0] else None
    random.seed(405)
    items = []
    for nm, ((cx, cy), (nx, ny)) in LEG.items():
        for i in range(7):
            f = random.uniform(0.0, 1.15)  # entre el punto de narracion y algo detras de la criatura
            x = nx + (cx - nx) * f + random.uniform(-350, 350); y = ny + (cy - ny) * f + random.uniform(-350, 350)
            z = gz(x, y)
            if z is None:
                continue
            for layer, hz in ((0, 18.0), (1, 45.0)):
                if layer == 1 and i % 2 == 0:
                    continue
                s = random.uniform(5.0, 7.5)
                items.append((x, y, z + hz, random.uniform(0, 360), s))
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "RELLENO_Neblina":
            unreal.EditorLevelLibrary.destroy_actor(a)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
    actor.set_actor_label("RELLENO_Neblina"); actor.tags = [unreal.Name("RELLENO")]
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
        new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
    comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(hh))
    comp.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Plane"))
    comp.set_material(0, m)
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_editor_property("cast_shadow", False)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property("can_ever_affect_navigation", False)
    comp.set_editor_property("instance_end_cull_distance", 4000)
    comp.add_instances([unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, yaw), unreal.Vector(s, s, 1.0)) for (x, y, z, yaw, s) in items], False, True)
    res["made"] = comp.get_instance_count()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))

