# 404_ue_cirios_cercania.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: los 8 cirios del Templo (Kit_Cirio, slot 0 = llama) se ENCIENDEN al acercarse el
#   visitante (<4.5 m): la llama crece desde la mecha (WPO colapsa la llama cuando esta lejos) y
#   titila (emisivo variable). Cada cirio por su propia distancia -> se encienden uno a uno
#   al recorrer la nave. Unlit, sin luces reales. Se reemplaza SOLO el slot 0 por instancia
#   (M_Flame original intacto) -> reversible.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cirios_res.json"
res = {"err": None, "assigned": []}
MAT = "/Game/JWN/FX/M_FlameCercania"
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        m = unreal.load_asset(MAT); mel.delete_all_material_expressions(m)
    else:
        m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_FlameCercania", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("two_sided", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1000, 0)
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -1000, 150)
    obj = mel.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -1000, 300)
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, 450)
    on_code = "float d = length((C - O).xy); return saturate((450.0 - d) / 150.0);"
    on1 = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 150)
    on1.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    on1.set_editor_property("code", on_code); on1.set_editor_property("inputs", [ci("C"), ci("O")])
    mel.connect_material_expressions(cam, "", on1, "C"); mel.connect_material_expressions(obj, "", on1, "O")
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 400)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float k = 1.0 - On;"
        "float3 base = float3(O.x, O.y, W.z - (W.z - (O.z + 125.0)) );"
        "float3 grow = (base - W) * k;"
        "float sway = sin(T * 9.0 + O.x * 0.01) * 0.35 * On * saturate((W.z - O.z - 128.0) / 10.0);"
        "return grow + float3(sway, sway * 0.6, 0.0);")
    wpo.set_editor_property("inputs", [ci("On"), ci("O"), ci("W"), ci("T")])
    mel.connect_material_expressions(on1, "", wpo, "On"); mel.connect_material_expressions(obj, "", wpo, "O")
    mel.connect_material_expressions(wp, "", wpo, "W"); mel.connect_material_expressions(t, "", wpo, "T")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    fl = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -150)
    fl.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    fl.set_editor_property("code",
        "float f = 0.82 + 0.12 * sin(T * 11.0 + O.y * 0.02) + 0.06 * sin(T * 23.0 + O.x * 0.03);"
        "return float3(1.0, 0.55, 0.15) * 9.0 * f * On;")
    fl.set_editor_property("inputs", [ci("T"), ci("O"), ci("On")])
    mel.connect_material_expressions(t, "", fl, "T"); mel.connect_material_expressions(obj, "", fl, "O")
    mel.connect_material_expressions(on1, "", fl, "On")
    mel.connect_material_property(fl, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    msk = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 150)
    msk.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    msk.set_editor_property("code", "return On > 0.02 ? 1.0 : 0.0;")
    msk.set_editor_property("inputs", [ci("On")])
    mel.connect_material_expressions(on1, "", msk, "On")
    mel.connect_material_property(msk, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("Cirio_"):
            c = a.get_component_by_class(unreal.StaticMeshComponent)
            c.set_material(0, m)
            res["assigned"].append([a.get_actor_label(), [ (c.get_material(i).get_name() if c.get_material(i) else None) for i in range(c.get_num_materials())]])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
