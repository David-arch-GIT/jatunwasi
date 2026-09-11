# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Lista las Texture2D y materiales de cada personaje importado para construir el material fantasmal con su textura real.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/texturas.json"
ar = unreal.AssetRegistryHelpers.get_asset_registry()
res = {}
for name in ["Duende", "Condenado", "Karisiri"]:
    base = "/Game/JWN/Apariciones/Anim/%s" % name
    texs = []; mats = []
    for d in ar.get_assets_by_path(base, recursive=True):
        cls = str(d.asset_class_path.asset_name)
        full = str(d.package_name) + "." + str(d.asset_name)
        if cls == "Texture2D": texs.append(full)
        elif "Material" in cls: mats.append(full)
    res[name] = {"texturas": texs, "materiales": mats}
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("TEXTURAS done")
