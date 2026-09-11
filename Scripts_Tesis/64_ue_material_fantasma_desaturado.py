# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Crea M_Aparicion3D_v2 (Unlit/Translucido) que DESATURA la textura (luminancia) y la tinta con un color fantasmal, para que las apariciones sean fantasmas monocromos palidos (no amarillos/garish). Reparenta las MI3D_* y reasigna. Emisivo = luminancia*Brillo*Tinte + Fresnel.
# Por que se necesito: El material a color salia amarillo garish; para "misterioso/fantasmal" conviene monocromo palido.
# Resultado obtenido: (pendiente) apariciones fantasmales palidas (verificar en PIE).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/material_v2.json"
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
FOLDER = "/Game/JWN/Blueprints"
MPATH = FOLDER + "/M_Aparicion3D_v2"

if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)
mat = tools.create_asset("M_Aparicion3D_v2", FOLDER, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("two_sided", True)

def ex(cls, x, y): return mel.create_material_expression(mat, cls, x, y)

tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -1000, -100); tex.set_editor_property("parameter_name", "BaseTex")
lumw = ex(unreal.MaterialExpressionConstant3Vector, -1000, 120); lumw.set_editor_property("constant", unreal.LinearColor(0.3, 0.59, 0.11, 1.0))
brillo = ex(unreal.MaterialExpressionScalarParameter, -1000, 260); brillo.set_editor_property("parameter_name", "Brillo"); brillo.set_editor_property("default_value", 1.4)
tint = ex(unreal.MaterialExpressionVectorParameter, -1000, 400); tint.set_editor_property("parameter_name", "Tinte"); tint.set_editor_property("default_value", unreal.LinearColor(0.7, 0.82, 0.95, 1.0))
opac = ex(unreal.MaterialExpressionScalarParameter, -1000, 620); opac.set_editor_property("parameter_name", "Opacity"); opac.set_editor_property("default_value", 0.6)

# luminancia = dot(tex.rgb, pesos)
dot = ex(unreal.MaterialExpressionDotProduct, -700, 0)
mel.connect_material_expressions(tex, "RGB", dot, "A")
mel.connect_material_expressions(lumw, "", dot, "B")
# lum * brillo
mlb = ex(unreal.MaterialExpressionMultiply, -500, 60)
mel.connect_material_expressions(dot, "", mlb, "A")
mel.connect_material_expressions(brillo, "", mlb, "B")
# * tinte
mt = ex(unreal.MaterialExpressionMultiply, -300, 120)
mel.connect_material_expressions(mlb, "", mt, "A")
mel.connect_material_expressions(tint, "", mt, "B")
emis = mt
try:
    fres = ex(unreal.MaterialExpressionFresnel, -700, 360); fres.set_editor_property("exponent", 4.0)
    mf = ex(unreal.MaterialExpressionMultiply, -500, 360)
    mel.connect_material_expressions(fres, "", mf, "A")
    mel.connect_material_expressions(tint, "", mf, "B")
    add = ex(unreal.MaterialExpressionAdd, -150, 150)
    mel.connect_material_expressions(mt, "", add, "A")
    mel.connect_material_expressions(mf, "", add, "B")
    emis = add
except Exception as e:
    res["fres"] = str(e)

mel.connect_material_property(emis, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.connect_material_property(opac, "", unreal.MaterialProperty.MP_OPACITY)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)

# Reparentar MIs + params por leyenda
CFG = {
    "MI3D_Karisiri":  {"tinte": (0.62, 0.78, 0.95), "b": 1.35, "o": 0.58},
    "MI3D_Condenado": {"tinte": (0.9, 0.82, 0.7),   "b": 1.35, "o": 0.58},
    "MI3D_Duende":    {"tinte": (0.7, 0.95, 0.72),  "b": 1.25, "o": 0.6},
}
for nm, c in CFG.items():
    mi = unreal.load_asset("/Game/JWN/Apariciones/" + nm)
    mel.set_material_instance_parent(mi, mat)
    mel.set_material_instance_scalar_parameter_value(mi, "Brillo", c["b"])
    mel.set_material_instance_scalar_parameter_value(mi, "Opacity", c["o"])
    mel.set_material_instance_vector_parameter_value(mi, "Tinte", unreal.LinearColor(c["tinte"][0], c["tinte"][1], c["tinte"][2], 1.0))
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Apariciones/" + nm)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("MATERIAL v2 desaturado listo")
