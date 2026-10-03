# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Importa el GLB del habito franciscano a /Game/JWN/Props/Convento/HabitoFranciscano con Interchange
#   (default). Luego reporta: assets creados, y para cada StaticMesh sus tris LOD0 y bounds (alto en cm, para verificar
#   ~175). Solo importa y mide. No coloca nada en el nivel todavia.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_habito.json"
res = {"creados": [], "meshes": [], "err": []}
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Content/JWN/Props/Convento/vestimenta y habito franciscano.glb"
DEST = "/Game/JWN/Props/Convento/HabitoFranciscano"
task = unreal.AssetImportTask()
task.set_editor_property("filename", SRC)
task.set_editor_property("destination_path", DEST)
task.set_editor_property("automated", True)
task.set_editor_property("save", True)
task.set_editor_property("replace_existing", True)
try:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = list(task.get_editor_property("imported_object_paths")) if task.get_editor_property("imported_object_paths") else []
    res["imported_paths"] = imported
except Exception as e:
    res["err"].append("import:" + str(e)[:80])
# listar lo que quedo en la carpeta
try:
    assets = unreal.EditorAssetLibrary.list_assets(DEST, recursive=True)
    res["creados"] = assets
    for p in assets:
        a = unreal.EditorAssetLibrary.load_asset(p)
        if isinstance(a, unreal.StaticMesh):
            b = a.get_bounds().box_extent  # half-extents
            res["meshes"].append({
                "path": p,
                "tris_lod0": a.get_num_triangles(0),
                "nlods": a.get_num_lods(),
                "alto_cm": round(b.z * 2, 1),
                "ancho_cm": round(b.x * 2, 1),
                "prof_cm": round(b.y * 2, 1),
                "n_materiales": len(a.static_materials)
            })
except Exception as e:
    res["err"].append("list:" + str(e)[:80])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("IMPORT HABITO meshes=%d" % len(res["meshes"]))
