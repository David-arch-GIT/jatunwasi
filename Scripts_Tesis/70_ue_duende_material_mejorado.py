# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Rehace M_Duende_AO con AO de mas contraste (Power) + color tierra mas rico y oscuro + rim Fresnel verdoso, para que el duende NO se vea uniforme/lavado sino con relieve y diseno.
# Por que se necesito: El duende se veia uniforme y feo (color plano); el usuario quiere que se vea texturizado/con diseno.
# Resultado obtenido: (pendiente) duende con relieve y color de diseno.
# ------------------------------------------------------------
import unreal, json
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
MPATH = "/Game/JWN/Blueprints/M_Duende_AO"
ao = unreal.load_asset("/Game/JWN/Apariciones/duende_uv/Duende_AO")
if ao is None:
    ao = unreal.load_asset("/Game/JWN/Apariciones/duende_uv/duende_uv/Textures/Duende_AO")

# recrear
if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)
mat = tools.create_asset("M_Duende_AO", "/Game/JWN/Blueprints", unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)

def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
aot = ex(unreal.MaterialExpressionTextureSampleParameter2D, -900, -50); aot.set_editor_property("parameter_name", "AO")
if ao: aot.set_editor_property("texture", ao)
# AO con contraste (Power ^1.8 => crevices mas oscuros)
pw = ex(unreal.MaterialExpressionPower, -650, -20)
mel.connect_material_expressions(aot, "RGB", pw, "Base")
pw.set_editor_property("const_exponent", 1.8)
col = ex(unreal.MaterialExpressionVectorParameter, -650, 170); col.set_editor_property("parameter_name", "Color"); col.set_editor_property("default_value", unreal.LinearColor(0.14, 0.11, 0.06, 1.0))
base = ex(unreal.MaterialExpressionMultiply, -400, 40)
mel.connect_material_expressions(pw, "", base, "A")
mel.connect_material_expressions(col, "", base, "B")
# emissive tenue
selfl = ex(unreal.MaterialExpressionScalarParameter, -650, 330); selfl.set_editor_property("parameter_name", "SelfLight"); selfl.set_editor_property("default_value", 0.42)
em = ex(unreal.MaterialExpressionMultiply, -250, 160)
mel.connect_material_expressions(base, "", em, "A")
mel.connect_material_expressions(selfl, "", em, "B")
emis = em
# rim fresnel verdoso (eerie)
try:
    fres = ex(unreal.MaterialExpressionFresnel, -650, 470); fres.set_editor_property("exponent", 4.0)
    rimc = ex(unreal.MaterialExpressionConstant3Vector, -650, 560); rimc.set_editor_property("constant", unreal.LinearColor(0.15, 0.35, 0.12, 1.0))
    rim = ex(unreal.MaterialExpressionMultiply, -400, 480)
    mel.connect_material_expressions(fres, "", rim, "A")
    mel.connect_material_expressions(rimc, "", rim, "B")
    add = ex(unreal.MaterialExpressionAdd, -120, 250)
    mel.connect_material_expressions(em, "", add, "A")
    mel.connect_material_expressions(rim, "", add, "B")
    emis = add
except Exception as e:
    res["fres"] = str(e)
mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(emis, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)

# reasignar a los duendes
try:
    acts = unreal.EditorActorSubsystem().get_all_level_actors()
except Exception:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
res["reasig"] = []
for a in acts:
    if a.get_actor_label() in ("App3D_Hac_Duende", "App3D_Plz_Duende"):
        a.get_component_by_class(unreal.StaticMeshComponent).set_material(0, mat)
        res["reasig"].append(a.get_actor_label())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/duende_mejor.json", "w").write(json.dumps(res))
unreal.log("duende mejorado")
