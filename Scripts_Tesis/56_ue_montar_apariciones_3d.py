# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Importa la textura verde del duende, crea 3 instancias de M_JW_Apparition (condenado/karisiri/duende) con su ApparitionTex, y en cada BP_Apparition cambia el Plane por el modelo 3D real: asigna malla + material, escala a altura realista, origen en base, sin colision, movable.
# Por que se necesito: Convertir las apariciones de billboards planos a modelos 3D reales, conservando el fundido/trigger existente.
# Resultado obtenido: (pendiente) apariciones 3D montadas.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/montar_apariciones.json"
DEST = "/Game/JWN/Apariciones"
BASE_MAT = unreal.load_asset("/Game/JWN/Blueprints/M_JW_Apparition")
res = {"pasos": []}

# 1) Importar textura verde del duende
task = unreal.AssetImportTask()
task.filename = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/T_Duende_Green.png"
task.destination_path = DEST + "/duende_color/Textures"
task.automated = True
task.replace_existing = True
task.save = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
res["pasos"].append("textura verde importada")

TEX = {
    "condenado": "/Game/JWN/Apariciones/condenado_opt/Textures/Image_0",
    "karisiri":  "/Game/JWN/Apariciones/karisiri_opt/Textures/Image_0",
    "duende":    "/Game/JWN/Apariciones/duende_color/Textures/T_Duende_Green",
}
MESH = {
    "condenado": "/Game/JWN/Apariciones/condenado_opt/StaticMeshes/condenado_opt",
    "karisiri":  "/Game/JWN/Apariciones/karisiri_opt/StaticMeshes/karisiri_opt",
    "duende":    "/Game/JWN/Apariciones/duende_color/StaticMeshes/duende_color",
}
ALTURA = {"condenado": 160.0, "karisiri": 185.0, "duende": 150.0}  # cm objetivo

tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

# 2) Crear instancias de material
MI = {}
for k, texpath in TEX.items():
    name = "MI_App_" + k.capitalize()
    path = DEST + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mi = tools.create_asset(name, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    mel.set_material_instance_parent(mi, BASE_MAT)
    tex = unreal.load_asset(texpath)
    if tex:
        mel.set_material_instance_texture_parameter_value(mi, "ApparitionTex", tex)
    mel.set_material_instance_scalar_parameter_value(mi, "Opacity", 1.0)
    unreal.EditorAssetLibrary.save_asset(mi.get_path_name())
    MI[k] = mi
    res["pasos"].append("MI creada: " + name + " tex=" + str(bool(tex)))

def mesh_height(sm):
    try:
        b = sm.get_bounding_box()  # Box (min,max)
        return b.max.z - b.min.z
    except Exception:
        try:
            mn, mx = sm.get_bounds().box_extent, None
            return sm.get_bounds().box_extent.z * 2.0
        except Exception:
            return 100.0

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

# 3) En cada BP_Apparition, cambiar Plane por modelo 3D
MAP = {"Condenado": "condenado", "Karisiri": "karisiri", "Duende": "duende"}
res["actores"] = []
for a in all_actors():
    if "Apparition" not in a.get_class().get_name():
        continue
    label = a.get_actor_label()
    key = None
    for tag, k in MAP.items():
        if tag.lower() in label.lower():
            key = k
            break
    if key is None:
        res["actores"].append({"label": label, "accion": "sin modelo (dejado)"})
        continue
    # localizar el StaticMeshComponent "Billboard"
    comp = None
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        comp = c
        break
    if comp is None:
        res["actores"].append({"label": label, "error": "sin StaticMeshComponent"})
        continue
    sm = unreal.load_asset(MESH[key])
    h = mesh_height(sm)
    s = ALTURA[key] / h if h > 1 else 1.0
    comp.set_editor_property("static_mesh", sm)
    comp.set_material(0, MI[key])
    try:
        comp.set_editor_property("relative_rotation", unreal.Rotator(0.0, 0.0, 0.0))
        comp.set_editor_property("relative_location", unreal.Vector(0.0, 0.0, 0.0))
        comp.set_world_scale3d(unreal.Vector(s, s, s))
    except Exception as e:
        res.setdefault("scale_err", []).append(str(e))
    comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    try:
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass
    # sombras off (Quest)
    try:
        comp.set_editor_property("cast_shadow", False)
    except Exception:
        pass
    res["actores"].append({"label": label, "modelo": key, "altura_nativa": round(h, 1), "escala": round(s, 3)})

# 4) Guardar
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    res["guardado"] = "ok"
except Exception as e:
    res["guardado"] = "err:" + str(e)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("MONTAR apariciones listo")
