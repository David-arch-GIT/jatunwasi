# 404b_ue_llamas_cirios.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (v2 de 404) Kit_Cirio no tiene llama pequena (su slot "FLAME" es el cuerpo de la vela),
#   asi que se restauro M_Flame y se agrega UNA LLAMITA (cono 3x9 cm) sobre la punta de cada uno
#   de los 8 cirios, en un HISM (RELLENO_LlamasCirios). M_FlameCercania: la llama crece desde su
#   centro y titila cuando el visitante esta a <4.5 m de ESE cirio (ObjectPositionWS por instancia)
#   -> se encienden uno a uno al recorrer la nave. Naranja (emisivo < saturacion), sin luces reales.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/llamas_cirios.json"
res = {"err": None}
MAT = "/Game/JWN/FX/M_FlameCercania"
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    m = unreal.load_asset(MAT); mel.delete_all_material_expressions(m)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1000, 0)
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -1000, 150)
    obj = mel.create_material_expression(m, unreal.MaterialExpressionTransformPosition, -1000, 300)
    obj.set_editor_property("transform_source_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_INSTANCE)
    obj.set_editor_property("transform_type", unreal.MaterialPositionTransformSource.TRANSFORMPOSSOURCE_WORLD)
    zero = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -1200, 300)
    zero.set_editor_property("constant", unreal.LinearColor(0, 0, 0, 0))
    mel.connect_material_expressions(zero, "", obj, "")
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 450)
    # NOTA: version superada por 404c (TransformPosition no da la posicion por instancia en HISM)
    on1 = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 150)
    on1.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    on1.set_editor_property("code", "float d = length((C - O).xy); return saturate((450.0 - d) / 150.0);")
    on1.set_editor_property("inputs", [ci("C"), ci("O")])
    mel.connect_material_expressions(cam, "", on1, "C"); mel.connect_material_expressions(obj, "", on1, "O")
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 400)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float k = 1.0 - On;"
        "float3 grow = (O - W) * k;"
        "float up = saturate((W.z - O.z) / 4.5);"
        "float sw = sin(T * 9.0 + O.x * 0.013) * 0.35 * On * up;"
        "float st = (0.12 * sin(T * 13.0 + O.y * 0.02)) * (W.z - O.z) * On;"
        "return grow + float3(sw, sw * 0.6, st);")
    wpo.set_editor_property("inputs", [ci("On"), ci("O"), ci("W"), ci("T")])
    mel.connect_material_expressions(on1, "", wpo, "On"); mel.connect_material_expressions(obj, "", wpo, "O")
    mel.connect_material_expressions(wp, "", wpo, "W"); mel.connect_material_expressions(t, "", wpo, "T")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    fl = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -150)
    fl.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    fl.set_editor_property("code",
        "float f = 0.85 + 0.10 * sin(T * 11.0 + O.y * 0.02) + 0.05 * sin(T * 23.0 + O.x * 0.03);"
        "float h = saturate((W.z - O.z + 4.5) / 9.0);"
        "float3 c = lerp(float3(1.0, 0.45, 0.05), float3(1.0, 0.85, 0.45), 1.0 - h);"
        "return c * 1.15 * f;")
    fl.set_editor_property("inputs", [ci("T"), ci("O"), ci("W")])
    mel.connect_material_expressions(t, "", fl, "T"); mel.connect_material_expressions(obj, "", fl, "O")
    mel.connect_material_expressions(wp, "", fl, "W")
    mel.connect_material_property(fl, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    msk = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 150)
    msk.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    msk.set_editor_property("code", "return On > 0.03 ? 1.0 : 0.0;")
    msk.set_editor_property("inputs", [ci("On")])
    mel.connect_material_expressions(on1, "", msk, "On")
    mel.connect_material_property(msk, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)

    tops = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("Cirio_"):
            L = a.get_actor_location(); tops.append((L.x, L.y, L.z + 147.0))
        if a.get_actor_label() == "RELLENO_LlamasCirios":
            unreal.EditorLevelLibrary.destroy_actor(a)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
    actor.set_actor_label("RELLENO_LlamasCirios"); actor.tags = [unreal.Name("RELLENO")]
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
        new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
    comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(hh))
    comp.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cone"))
    comp.set_material(0, m)
    comp.set_mobility(unreal.ComponentMobility.STATIC)
    comp.set_editor_property("cast_shadow", False)
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    comp.set_editor_property("can_ever_affect_navigation", False)
    comp.set_editor_property("instance_end_cull_distance", 2500)
    comp.set_editor_property("bounds_scale", 3.0)
    comp.add_instances([unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0), unreal.Vector(0.03, 0.03, 0.09)) for (x, y, z) in tops], False, True)
    res["made"] = comp.get_instance_count()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))


