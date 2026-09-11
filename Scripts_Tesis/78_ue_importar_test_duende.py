# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) PRUEBA importar duende_animado.glb como skeletal mesh via AssetImportTask/Interchange. Reporta que assets se crearon (mesh/skeleton/anim/material) a JSON.
# Por que: Confirmar que el import de glTF con esqueleto funciona por Python antes de importar los 6.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_test.json"
res = {"imported": [], "err": None}
GLB = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/duende_animado.glb"
DEST = "/Game/JWN/Apariciones/Anim/Duende"
try:
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", GLB)
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    task.set_editor_property("replace_existing", True)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.import_asset_tasks([task])
    paths = list(task.get_editor_property("imported_object_paths"))
    for p in paths:
        a = unreal.load_asset(p)
        res["imported"].append({"path": p, "class": a.get_class().get_name() if a else "None"})
except Exception as e:
    res["err"] = str(e)
# listar lo que quedo en la carpeta destino
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for d in ar.get_assets_by_path(DEST, recursive=True):
        res.setdefault("folder", []).append("%s [%s]" % (str(d.asset_name), str(d.asset_class_path.asset_name)))
except Exception as e:
    res["folder_err"] = str(e)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("IMPORT TEST done: %d objs, err=%s" % (len(res["imported"]), res["err"]))
