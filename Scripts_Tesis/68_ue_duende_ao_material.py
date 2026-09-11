# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Importa duende_uv (malla con UVs) + Duende_AO. Crea M_Duende_AO (color tierra x AO + leve auto-brillo, lit) y lo aplica a los App3D_*_Duende (cambia la malla a la UV y el material). Asi el duende tiene relieve/diseno, no plano.
# Por que se necesito: El duende no tenia textura; se le da profundidad con AO + color de diseno.
# Resultado obtenido: (pendiente) duendes con material AO.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/duende_ao.json"
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
DEST = "/Game/JWN/Apariciones/duende_uv"

# 1) importar malla + AO
for f in ["duende_uv.glb", "Duende_AO.png"]:
    task = unreal.AssetImportTask()
    task.filename = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/" + f
    task.destination_path = DEST
    task.automated = True
    task.replace_existing = True
    task.save = True
    tools.import_asset_tasks([task])

ao = unreal.load_asset(DEST + "/Duende_AO")
mesh = None
for cand in ["/StaticMeshes/duende_uv", "/duende_uv"]:
    if unreal.EditorAssetLibrary.does_asset_exist(DEST + cand):
        mesh = unreal.load_asset(DEST + cand); break
res["mesh_ok"] = mesh is not None
res["ao_ok"] = ao is not None

# 2) material M_Duende_AO (tierra x AO + emissive lit)
MPATH = "/Game/JWN/Blueprints/M_Duende_AO"
if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)
mat = tools.create_asset("M_Duende_AO", "/Game/JWN/Blueprints", unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)

def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
aot = ex(unreal.MaterialExpressionTextureSampleParameter2D, -750, -50); aot.set_editor_property("parameter_name", "AO")
if ao:
    aot.set_editor_property("texture", ao)
col = ex(unreal.MaterialExpressionVectorParameter, -750, 180); col.set_editor_property("parameter_name", "Color"); col.set_editor_property("default_value", unreal.LinearColor(0.16, 0.19, 0.11, 1.0))
selfl = ex(unreal.MaterialExpressionScalarParameter, -750, 340); selfl.set_editor_property("parameter_name", "SelfLight"); selfl.set_editor_property("default_value", 0.55)
base = ex(unreal.MaterialExpressionMultiply, -450, 60)
mel.connect_material_expressions(aot, "RGB", base, "A")
mel.connect_material_expressions(col, "", base, "B")
emis = ex(unreal.MaterialExpressionMultiply, -250, 180)
mel.connect_material_expressions(base, "", emis, "A")
mel.connect_material_expressions(selfl, "", emis, "B")
mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(emis, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)

# 3) aplicar a los App3D duende (cambiar malla a la UV + material)
try:
    acts = unreal.EditorActorSubsystem().get_all_level_actors()
except Exception:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
res["aplicados"] = []
for a in acts:
    l = a.get_actor_label()
    if l in ("App3D_Hac_Duende", "App3D_Plz_Duende"):
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        if mesh:
            c.set_editor_property("static_mesh", mesh)
        c.set_material(0, mat)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_editor_property("cast_shadow", False)
        res["aplicados"].append(l)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("duende AO listo")
