import unreal, json, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fotos_import.json"
res = {"texturas": [], "instancias": [], "err": []}
SRCDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano"
DEST = "/Game/FotosAntano/Imported"
at = unreal.AssetToolsHelpers.get_asset_tools()
# 1) importar cada .jpg como Texture2D
jpgs = [f for f in os.listdir(SRCDIR) if f.lower().endswith(".jpg")]
tex_assets = []
for f in jpgs:
    try:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", os.path.join(SRCDIR, f))
        task.set_editor_property("destination_path", DEST)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", True)
        at.import_asset_tasks([task])
        imp = list(task.get_editor_property("imported_object_paths"))
        for p in imp:
            a = unreal.EditorAssetLibrary.load_asset(p.split(".")[0] if "." in p.split("/")[-1] else p)
            if isinstance(a, unreal.Texture2D):
                a.set_editor_property("max_texture_size", 1024)  # fotos de cuadro, 1024 sobra
                unreal.EditorAssetLibrary.save_asset(a.get_path_name().split(".")[0], only_if_is_dirty=False)
                tex_assets.append((f, a))
                res["texturas"].append(f + " -> " + a.get_name())
    except Exception as e:
        res["err"].append("imp "+f[:20]+":"+str(e)[:40])
# 2) material base con parametro de textura -> BaseColor + Emissive (visible en la penumbra)
MEL = unreal.MaterialEditingLibrary
matpath = "/Game/FotosAntano/M_FotoAntano"
if unreal.EditorAssetLibrary.does_asset_exist(matpath):
    unreal.EditorAssetLibrary.delete_asset(matpath)
mat = at.create_asset("M_FotoAntano", "/Game/FotosAntano", unreal.Material, unreal.MaterialFactoryNew())
tp = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -450, 0)
tp.set_editor_property("parameter_name", "Foto")
if tex_assets: tp.set_editor_property("texture", tex_assets[0][1])
MEL.connect_material_property(tp, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, 260)
MEL.connect_material_expressions(tp, "RGB", mul, "A")
mul.set_editor_property("const_b", 0.55)
MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
try: mat.set_editor_property("two_sided", False)
except Exception: pass
MEL.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(matpath, only_if_is_dirty=False)
res["material"] = "M_FotoAntano ok"
# 3) una Material Instance por foto
for (f, tex) in tex_assets:
    nm = "MI_Foto_" + tex.get_name()[:24]
    ip = "/Game/FotosAntano/"+nm
    if unreal.EditorAssetLibrary.does_asset_exist(ip): unreal.EditorAssetLibrary.delete_asset(ip)
    mi = at.create_asset(nm, "/Game/FotosAntano", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, mat)
    MEL.set_material_instance_texture_parameter_value(mi, "Foto", tex)
    unreal.EditorAssetLibrary.save_asset(ip, only_if_is_dirty=False)
    res["instancias"].append(nm)
open(OUT, "w").write(json.dumps(res, indent=1))
