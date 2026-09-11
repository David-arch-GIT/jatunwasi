# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Importa los 3 *_full.glb (mesh+esqueleto+2 anims Idle/Walk) a /Game/JWN/Apariciones/Anim/<Char>. Reporta assets creados (mesh, skeleton, anims, material) a JSON.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_full.json"
BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
CHARS = ["duende", "condenado", "karisiri"]
res = {}
tools = unreal.AssetToolsHelpers.get_asset_tools()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for name in CHARS:
    dest = "/Game/JWN/Apariciones/Anim/%s" % name.capitalize()
    try:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", BASE + name + "_full.glb")
        t.set_editor_property("destination_path", dest)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        t.set_editor_property("replace_existing", True)
        tools.import_asset_tasks([t])
        info = {"mesh": None, "skeleton": None, "anims": [], "mats": []}
        for d in ar.get_assets_by_path(dest, recursive=True):
            cls = str(d.asset_class_path.asset_name); nm = str(d.asset_name)
            full = str(d.package_name) + "." + nm
            if cls == "SkeletalMesh": info["mesh"] = full
            elif cls == "Skeleton": info["skeleton"] = full
            elif cls == "AnimSequence": info["anims"].append(full)
            elif "Material" in cls: info["mats"].append(full)
        res[name] = info
    except Exception as e:
        res[name] = {"err": str(e)}
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("IMPORT FULL done")
