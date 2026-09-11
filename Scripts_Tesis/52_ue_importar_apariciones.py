# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE via MCPUnreal) Importa los 3 GLB optimizados a /Game/JWN/Apariciones y reporta los assets creados.
# Por que se necesito: Traer las apariciones optimizadas al proyecto para colocarlas y animarlas.
# Resultado obtenido: (pendiente) mallas + materiales importados.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_apariciones.json"
DEST = "/Game/JWN/Apariciones"
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
FILES = ["condenado_opt.glb", "karisiri_opt.glb", "duende_color.glb"]

tools = unreal.AssetToolsHelpers.get_asset_tools()
res = {"importados": []}

for fn in FILES:
    task = unreal.AssetImportTask()
    task.filename = SRC + fn
    task.destination_path = DEST
    task.automated = True
    task.replace_existing = True
    task.save = True
    try:
        tools.import_asset_tasks([task])
        paths = list(task.get_editor_property("imported_object_paths"))
        res["importados"].append({"archivo": fn, "assets": paths})
    except Exception as e:
        res["importados"].append({"archivo": fn, "error": str(e)})

# listar lo que quedo en la carpeta
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = ar.get_assets_by_path(DEST, recursive=True)
    res["carpeta"] = []
    for a in assets:
        res["carpeta"].append(str(a.asset_name) + " [" + str(a.asset_class_path.asset_name) + "]")
except Exception as e:
    res["carpeta_err"] = str(e)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("IMPORT apariciones listo")
