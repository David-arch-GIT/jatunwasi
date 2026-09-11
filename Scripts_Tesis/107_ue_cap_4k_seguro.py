# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Capa SOLO las texturas >2048 (las ~166 de 4K) que revientan la memoria del Quest (4.2GB).
#   Impostores -> 512 (se ven de lejos), resto 4K -> 1024. Usa AssetRegistry para listar (sin cargar todo),
#   carga SOLO esas ~166, y GUARDA una por una (save_asset por path = confiable, evita el bug de lote).
#   Escribe progreso incremental por si hay timeout. NO toca geometria/luces/look de cerca.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_4k.json"
res = {"objetivo": 0, "capadas": 0, "guardadas": 0, "err": 0, "hechas": []}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
tex = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
targets = []
for d in tex:
    p = str(d.package_name)
    if not p.startswith("/Game/"):
        continue
    dim = d.get_tag_value("Dimensions")
    if not dim:
        continue
    try:
        parts = str(dim).replace("X", "x").split("x")
        w = int(parts[0]); h = int(parts[1])
    except Exception:
        continue
    if max(w, h) > 2048:
        targets.append((p + "." + str(d.asset_name), str(d.asset_name)))
res["objetivo"] = len(targets)

def write():
    open(OUT, "w").write(json.dumps(res, indent=1))
write()

for i, (path, name) in enumerate(targets):
    try:
        t = unreal.load_asset(path)
        if t is None:
            res["err"] += 1
            continue
        cap = 512 if "impostor" in name.lower() else 1024
        cur = int(t.get_editor_property("max_texture_size"))
        if cur == 0 or cur > cap:
            t.set_editor_property("max_texture_size", cap)
            res["capadas"] += 1
        # guardar por path (confiable)
        ok = unreal.EditorAssetLibrary.save_asset(path, False)
        if ok:
            res["guardadas"] += 1
    except Exception:
        res["err"] += 1
    if (i + 1) % 15 == 0:
        res["hechas"].append(i + 1)
        write()

write()
unreal.log("CAP 4K objetivo=%d capadas=%d guardadas=%d err=%d" % (res["objetivo"], res["capadas"], res["guardadas"], res["err"]))
