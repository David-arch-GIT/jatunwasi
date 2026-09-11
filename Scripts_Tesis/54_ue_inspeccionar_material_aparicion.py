# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Localiza M_JW_Apparition y vuelca sus parametros (escalar/vector/textura), blend mode, shading model, two-sided. Tambien confirma rutas de las mallas/texturas nuevas.
# Por que se necesito: Saber que parametro usa el fundido para conservar textura + efecto al cambiar el plane por el modelo 3D.
# Resultado obtenido: (pendiente) parametros del material de aparicion.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspect_material.json"
res = {}

ar = unreal.AssetRegistryHelpers.get_asset_registry()

# Buscar M_JW_Apparition
found = None
for a in ar.get_all_assets():
    if a.asset_name == "M_JW_Apparition":
        found = str(a.package_name)
        break
res["path"] = found

def dump_params(mat):
    d = {}
    try:
        mel = unreal.MaterialEditingLibrary
        d["scalar"] = list(mel.get_scalar_parameter_names(mat))
        d["vector"] = list(mel.get_vector_parameter_names(mat))
        d["texture"] = list(mel.get_texture_parameter_names(mat))
        d["static_switch"] = list(mel.get_static_switch_parameter_names(mat))
    except Exception as e:
        d["err"] = str(e)
    return d

if found:
    mat = unreal.load_asset(found)
    res["clase"] = mat.get_class().get_name()
    # si es material base
    try:
        res["blend_mode"] = str(mat.get_editor_property("blend_mode"))
        res["shading_model"] = str(mat.get_editor_property("shading_model"))
        res["two_sided"] = bool(mat.get_editor_property("two_sided"))
    except Exception as e:
        res["base_props_err"] = str(e)
    res["params"] = dump_params(mat)
    # si es instancia, ver su parent
    try:
        if isinstance(mat, unreal.MaterialInstanceConstant):
            res["parent"] = mat.get_editor_property("parent").get_path_name()
    except Exception:
        pass

# confirmar rutas nuevas
res["mallas"] = {
    "condenado": unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Apariciones/condenado_opt/StaticMeshes/condenado_opt"),
    "karisiri": unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Apariciones/karisiri_opt/StaticMeshes/karisiri_opt"),
    "duende": unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Apariciones/duende_color/StaticMeshes/duende_color"),
}
res["texturas"] = {
    "condenado_Image_0": unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Apariciones/condenado_opt/Textures/Image_0"),
    "karisiri_Image_0": unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Apariciones/karisiri_opt/Textures/Image_0"),
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("INSPECT material aparicion listo")
