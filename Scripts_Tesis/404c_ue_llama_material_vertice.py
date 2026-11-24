# 404c_ue_llama_material_vertice.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: corregir M_FlameCercania. ObjectPositionWS / TransformPosition(Local|Instance) NO dan la
#   posicion por instancia en HISM en esta version -> la llama siempre quedaba "lejos" (apagada).
#   Ahora: distancia con WorldPosition del vertice (llama de 9 cm -> error nulo) y crecimiento con
#   la posicion LOCAL del cono (PreSkinnedLocalPosition) usando la escala conocida (0.03,0.03,0.09),
#   colapsando hacia la base del cono. Degradado: base amarillo-blanca, punta naranja. Titileo.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/llama_v3.json"
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
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 300)
    lp = mel.create_material_expression(m, unreal.MaterialExpressionPreSkinnedPosition, -1000, 450)
    on1 = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 150)
    on1.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    on1.set_editor_property("code", "float d = length((C - W).xy); return saturate((450.0 - d) / 150.0);")
    on1.set_editor_property("inputs", [ci("C"), ci("W")])
    mel.connect_material_expressions(cam, "", on1, "C"); mel.connect_material_expressions(wp, "", on1, "W")
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 400)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float k = 1.0 - On;"
        "float h = saturate((L.z + 50.0) / 100.0);"
        "float3 g = -float3(L.x * 0.03, L.y * 0.03, (L.z + 50.0) * 0.09) * k;"
        "float sw = sin(T * 9.0 + W.x * 0.013) * 0.4 * On * h;"
        "float st = 0.15 * sin(T * 13.0 + W.y * 0.02) * (L.z + 50.0) * 0.09 * On;"
        "return g + float3(sw, sw * 0.6, st);")
    wpo.set_editor_property("inputs", [ci("On"), ci("L"), ci("W"), ci("T")])
    mel.connect_material_expressions(on1, "", wpo, "On"); mel.connect_material_expressions(lp, "", wpo, "L")
    mel.connect_material_expressions(wp, "", wpo, "W"); mel.connect_material_expressions(t, "", wpo, "T")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    fl = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -150)
    fl.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    fl.set_editor_property("code",
        "float f = 0.85 + 0.10 * sin(T * 11.0 + W.y * 0.02) + 0.05 * sin(T * 23.0 + W.x * 0.03);"
        "return float3(1.0, 0.58, 0.12) * 1.1 * f;")
    fl.set_editor_property("inputs", [ci("T"), ci("W")])
    mel.connect_material_expressions(t, "", fl, "T")
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
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "RELLENO_LlamasCirios":
            a.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent).set_material(0, m)
            res["assigned"] = True
    if unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/FX/M_TestNaranja"):
        unreal.EditorAssetLibrary.delete_asset("/Game/JWN/FX/M_TestNaranja")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
