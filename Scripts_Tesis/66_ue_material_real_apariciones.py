# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Crea M_Aparicion_Real (Default Lit, Opaco) que muestra la TEXTURA REAL como Base Color + un leve auto-brillo (Emissive = Tex*SelfLight) para verse de noche SIN agregar luces reales. Reasigna Karisiri y Condenado (que tienen textura de fotogrametria). Asi se ven ORIGINALES, no amarillo lavado.
# Por que se necesito: El material unlit emisivo quemaba la textura ("orinado"); el usuario quiere el look original real.
# Resultado obtenido: (pendiente) apariciones con su textura real, visibles.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mat_real2.json"
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
MPATH = "/Game/JWN/Blueprints/M_Aparicion_Real"
if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)
mat = tools.create_asset("M_Aparicion_Real", "/Game/JWN/Blueprints", unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)

def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -700, -50); tex.set_editor_property("parameter_name", "BaseTex")
selfl = ex(unreal.MaterialExpressionScalarParameter, -700, 220); selfl.set_editor_property("parameter_name", "SelfLight"); selfl.set_editor_property("default_value", 0.7)
rough = ex(unreal.MaterialExpressionScalarParameter, -700, 340); rough.set_editor_property("parameter_name", "Rough"); rough.set_editor_property("default_value", 0.85)
emis = ex(unreal.MaterialExpressionMultiply, -400, 120)
mel.connect_material_expressions(tex, "RGB", emis, "A")
mel.connect_material_expressions(selfl, "", emis, "B")
mel.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(emis, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)

# MIs reales con la textura de cada uno
TEX = {
    "Karisiri":  "/Game/JWN/Apariciones/karisiri_opt/Textures/Image_0",
    "Condenado": "/Game/JWN/Apariciones/condenado_opt/Textures/Image_0",
}
MI = {}
for k, tp in TEX.items():
    name = "MIR_" + k
    p = "/Game/JWN/Apariciones/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        unreal.EditorAssetLibrary.delete_asset(p)
    mi = tools.create_asset(name, "/Game/JWN/Apariciones", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    t = unreal.load_asset(tp)
    if t:
        mel.set_material_instance_texture_parameter_value(mi, "BaseTex", t)
    unreal.EditorAssetLibrary.save_asset(p)
    MI[k] = mi

# reasignar a los actores
try:
    acts = unreal.EditorActorSubsystem().get_all_level_actors()
except Exception:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
res["reasig"] = []
for a in acts:
    l = a.get_actor_label()
    if not l.startswith("App3D_"):
        continue
    for k in MI:
        if k.lower() in l.lower():
            a.get_component_by_class(unreal.StaticMeshComponent).set_material(0, MI[k])
            res["reasig"].append(l)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res))
unreal.log("material real listo")
