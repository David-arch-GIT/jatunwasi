# 403_ue_luces_animas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: "luces de las animas" junto al condenado (folklore andino: almas que lo acompanan).
#   Orbes azul palido, deriva lenta por instancia y pulso suave. Al acercarse la camara a <5 m
#   cada orbe se APARTA (empuje alejandose de la camara y hacia arriba). Todo en material (WPO
#   con ObjectPositionWS de la instancia + CameraPositionWS). Unlit aditivo, sin luces reales.
#   Actor RELLENO_Animas (tag RELLENO).
import unreal, json, math, random, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/animas.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"err": None}
MAT = "/Game/JWN/FX/M_Animas"
MESH = "/Game/StylescapeHD/Foliage/Forest/SM_ForestRock_04"
CENTER = (1031.0, 8380.0)
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        m = unreal.load_asset(MAT); mel.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Animas", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1000, 0)
    r = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -1000, 150)
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -1000, 300)
    # posicion por vertice (orbe de ~7 cm): ObjectPositionWS en HISM da el centro del grupo, no la instancia
    obj = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 450)
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -600, 300)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float tt = T * (0.25 + R * 0.25); float a = R * 41.3; float b = R * 17.9;"
        "float3 w = float3(sin(tt*0.41+a)*60.0 + sin(tt*0.93+b)*20.0, cos(tt*0.33+b)*60.0 + sin(tt*0.71+a)*20.0, sin(tt*0.57+a)*35.0);"
        "float3 v = O - C; float d = length(v.xy); float2 dir = d > 1.0 ? v.xy / d : float2(1.0, 0.0);"
        "float k = saturate((500.0 - d) / 350.0); k = k * k;"
        "return w + float3(dir * 320.0 * k, 160.0 * k);")
    wpo.set_editor_property("inputs", [ci("T"), ci("R"), ci("C"), ci("O")])
    mel.connect_material_expressions(t, "", wpo, "T"); mel.connect_material_expressions(r, "", wpo, "R")
    mel.connect_material_expressions(cam, "", wpo, "C"); mel.connect_material_expressions(obj, "", wpo, "O")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    br = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -600, -150)
    br.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    br.set_editor_property("code", "return 0.45 + 0.35 * sin(T * (0.6 + R * 0.5) + R * 50.0);")
    br.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", br, "T"); mel.connect_material_expressions(r, "", br, "R")
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -600, -400); fr.set_editor_property("exponent", 1.2)
    om = mel.create_material_expression(m, unreal.MaterialExpressionOneMinus, -400, -400)
    mel.connect_material_expressions(fr, "", om, "")
    col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -600, -600)
    col.set_editor_property("constant", unreal.LinearColor(0.25, 0.55, 1.0, 1.0))
    m1 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -250)
    mel.connect_material_expressions(col, "", m1, "A"); mel.connect_material_expressions(br, "", m1, "B")
    m2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -150, -300)
    mel.connect_material_expressions(m1, "", m2, "A"); mel.connect_material_expressions(om, "", m2, "B")
    m3 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, 0, -300); m3.set_editor_property("const_b", 3.5)
    mel.connect_material_expressions(m2, "", m3, "A")
    mel.connect_material_property(m3, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)

    random.seed(403)
    pts = []
    while len(pts) < 30:
        ang = random.uniform(0, 6.283); rr = random.uniform(150, 700)
        x = CENTER[0] + math.cos(ang) * rr; y = CENTER[1] + math.sin(ang) * rr
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        tp = h.to_tuple()
        if not tp[0]:
            continue
        pts.append((x, y, tp[4].z + random.uniform(50, 190), random.uniform(0.13, 0.2)))
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "RELLENO_Animas":
            unreal.EditorLevelLibrary.destroy_actor(a)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
    actor.set_actor_label("RELLENO_Animas"); actor.tags = [unreal.Name("RELLENO")]
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
        new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
    comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(hh))
    comp.set_static_mesh(unreal.load_asset(MESH))
    for i in range(comp.get_num_materials()):
        comp.set_material(i, m)
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_editor_property("cast_shadow", False)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property("can_ever_affect_navigation", False)
    comp.set_editor_property("instance_end_cull_distance", 4500)
    comp.set_editor_property("bounds_scale", 40.0)
    comp.add_instances([unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0), unreal.Vector(s, s, s)) for (x, y, z, s) in pts], False, True)
    res["made"] = comp.get_instance_count()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))



