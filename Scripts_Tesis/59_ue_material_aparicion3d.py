# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Crea M_Aparicion3D (Unlit/Translucido/two-sided) con emisivo = Textura*Brillo*Tinte + borde Fresnel, y Opacity param. Crea 3 instancias (Karisiri/Condenado/Duende) y las asigna a los App3D_*. Deja apariciones etereas que brillan de noche y pueden hacer fundido.
# Por que se necesito: El material viejo salia negro; se necesita un fantasma emisivo visible y controlable.
# Resultado obtenido: (pendiente) material + instancias + apariciones brillando.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/material3d.json"
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
FOLDER = "/Game/JWN/Blueprints"
MPATH = FOLDER + "/M_Aparicion3D"

if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)

mat = tools.create_asset("M_Aparicion3D", FOLDER, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("two_sided", True)

def ex(cls, x, y):
    return mel.create_material_expression(mat, cls, x, y)

tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -900, -100)
tex.set_editor_property("parameter_name", "BaseTex")
brillo = ex(unreal.MaterialExpressionScalarParameter, -900, 150)
brillo.set_editor_property("parameter_name", "Brillo"); brillo.set_editor_property("default_value", 1.8)
tint = ex(unreal.MaterialExpressionVectorParameter, -900, 300)
tint.set_editor_property("parameter_name", "Tinte"); tint.set_editor_property("default_value", unreal.LinearColor(0.75, 0.85, 1.0, 1.0))
opac = ex(unreal.MaterialExpressionScalarParameter, -900, 520)
opac.set_editor_property("parameter_name", "Opacity"); opac.set_editor_property("default_value", 0.9)

mul1 = ex(unreal.MaterialExpressionMultiply, -600, 0)
mel.connect_material_expressions(tex, "RGB", mul1, "A")
mel.connect_material_expressions(brillo, "", mul1, "B")
mul2 = ex(unreal.MaterialExpressionMultiply, -400, 50)
mel.connect_material_expressions(mul1, "", mul2, "A")
mel.connect_material_expressions(tint, "", mul2, "B")

emis = mul2
try:
    fres = ex(unreal.MaterialExpressionFresnel, -600, 350)
    fres.set_editor_property("exponent", 3.5)
    mul3 = ex(unreal.MaterialExpressionMultiply, -400, 350)
    mel.connect_material_expressions(fres, "", mul3, "A")
    mel.connect_material_expressions(tint, "", mul3, "B")
    add = ex(unreal.MaterialExpressionAdd, -200, 120)
    mel.connect_material_expressions(mul2, "", add, "A")
    mel.connect_material_expressions(mul3, "", add, "B")
    emis = add
    res["fresnel"] = "ok"
except Exception as e:
    res["fresnel"] = "skip:" + str(e)

mel.connect_material_property(emis, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.connect_material_property(opac, "", unreal.MaterialProperty.MP_OPACITY)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)
res["material"] = MPATH

# Instancias
INST = {
    "Karisiri":  {"tex": "/Game/JWN/Apariciones/karisiri_opt/Textures/Image_0",  "tinte": (0.75, 0.85, 1.0), "brillo": 1.9},
    "Condenado": {"tex": "/Game/JWN/Apariciones/condenado_opt/Textures/Image_0", "tinte": (1.0, 0.75, 0.65), "brillo": 1.9},
    "Duende":    {"tex": "/Game/JWN/Apariciones/duende_color/Textures/T_Duende_Green", "tinte": (0.8, 1.0, 0.8), "brillo": 1.6},
}
MI = {}
for k, c in INST.items():
    name = "MI3D_" + k
    p = "/Game/JWN/Apariciones/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        unreal.EditorAssetLibrary.delete_asset(p)
    mi = tools.create_asset(name, "/Game/JWN/Apariciones", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, mat)
    t = unreal.load_asset(c["tex"])
    if t:
        mel.set_material_instance_texture_parameter_value(mi, "BaseTex", t)
    mel.set_material_instance_vector_parameter_value(mi, "Tinte", unreal.LinearColor(c["tinte"][0], c["tinte"][1], c["tinte"][2], 1.0))
    mel.set_material_instance_scalar_parameter_value(mi, "Brillo", c["brillo"])
    mel.set_material_instance_scalar_parameter_value(mi, "Opacity", 0.9)
    unreal.EditorAssetLibrary.save_asset(p)
    MI[k] = mi

# Reasignar a los App3D_*
try:
    acts = unreal.EditorActorSubsystem().get_all_level_actors()
except Exception:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
res["reasignados"] = []
for a in acts:
    lab = a.get_actor_label()
    if not lab.startswith("App3D_"):
        continue
    key = None
    for k in MI:
        if k.lower() in lab.lower():
            key = k
            break
    if key is None:
        continue
    smc = a.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, MI[key])
    res["reasignados"].append({"actor": lab, "mi": MI[key].get_name()})

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("MATERIAL3D listo")
