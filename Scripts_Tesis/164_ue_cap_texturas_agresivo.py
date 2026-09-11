# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) Re-capa las texturas de source 4096 al estado AGRESIVO ya VALIDADO en visor (build25 "esta bello"):
#   impostores (billboards) -> 512, resto naturaleza/roca/corteza/adoquin/canyon -> 1024. Ahorra ~180MB de datos de
#   textura vs el cap conservador (build51 1024/2048). NO toca HERO ni nada <4096. Uno-por-uno via AssetRegistry,
#   guardado incremental. Reemplaza el 163. Escribe JSON de progreso.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_agresivo_progreso.json"
res = {"a512": [], "a1024": [], "saltadas_hero": [], "err": [], "hecho": 0}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
HERO = ["santo","saint","virgen","museo","museum","retrato","portrait","skin","piel","_face","cloth","tela",
        "vestiment","fabric","duende","karisiri","condenado","apparition","aparicion"]
tex = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
targets = []
for a in tex:
    pkg = str(a.package_name)
    if not pkg.startswith("/Game"):
        continue
    dim = a.get_tag_value("Dimensions"); w = 0
    if dim:
        try:
            w = int(str(dim).lower().replace(" ", "").split("x")[0])
        except Exception:
            pass
    if w < 4096:
        continue
    targets.append(pkg)
def cap_one(pkg):
    low = pkg.split("/")[-1].lower()
    if any(k in low for k in HERO):
        res["saltadas_hero"].append(pkg.split("/")[-1]); return
    try:
        t = unreal.EditorAssetLibrary.load_asset(pkg)
        if not t:
            res["err"].append("noload:" + pkg[-28:]); return
        if "impostor" in low:
            size = 512; bucket = "a512"
        else:
            size = 1024; bucket = "a1024"
        t.set_editor_property("max_texture_size", size)
        unreal.EditorAssetLibrary.save_asset(pkg, only_if_is_dirty=False)
        res[bucket].append(pkg.split("/")[-1])
        res["hecho"] += 1
    except Exception as e:
        res["err"].append(pkg[-24:] + ":" + str(e)[:36])
for i, p in enumerate(targets):
    cap_one(p)
    if i % 25 == 0:
        open(OUT, "w").write(json.dumps(res, indent=1))
res["n_targets"] = len(targets)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CAP AGRESIVO hecho=%d 512=%d 1024=%d err=%d" % (res["hecho"], len(res["a512"]), len(res["a1024"]), len(res["err"])))
