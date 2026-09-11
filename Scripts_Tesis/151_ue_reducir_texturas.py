# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) ANTI-CUELGUE por RAM. Cap de tamano en texturas 4096 SOBREDIMENSIONADAS y de uso seguro: impostors de
#   arbol (billboards lejanos) -> 1024; tocon/roca/cerca de piedra/acantilado/duende -> 2048. Alinea con la regla del
#   proyecto (<=2K Quest). NO toca texturas de edificios/santos/museo (hero, up-close). Carga solo las que matchean
#   (~20, no miles). Guarda cada asset.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reducir_tex.json"
res = {"a1024": [], "a2048": [], "err": []}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
TREE = ["tropicaltree","oak_","maple","_tree_","birch","willow"]
GROUND2K = ["t_stump","t_rocks","t_stone_fence","t_rockycliff","texture_20250901"]
tex = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Texture2D"), True)
targets_1024=[]; targets_2048=[]
for a in tex:
    pkg=str(a.package_name)
    if not pkg.startswith("/Game"): continue
    nm=str(a.asset_name); low=nm.lower()
    dim=a.get_tag_value("Dimensions"); w=0
    if dim:
        try: w=int(str(dim).lower().replace(" ","").split("x")[0])
        except Exception: pass
    if w<4096: continue
    if "impostor" in low and any(k in low for k in TREE):
        targets_1024.append(pkg)
    elif any(k in low for k in GROUND2K):
        targets_2048.append(pkg)
def cap(pkg, size, bucket):
    try:
        t=unreal.EditorAssetLibrary.load_asset(pkg)
        if not t: res["err"].append("noload:"+pkg[-30:]); return
        t.set_editor_property("max_texture_size", size)
        unreal.EditorAssetLibrary.save_asset(pkg, only_if_is_dirty=False)
        res[bucket].append(pkg.split("/")[-1])
    except Exception as e:
        res["err"].append(pkg[-24:]+":"+str(e)[:40])
for p in targets_1024: cap(p,1024,"a1024")
for p in targets_2048: cap(p,2048,"a2048")
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("REDUCIR TEX 1024=%d 2048=%d" % (len(res["a1024"]),len(res["a2048"])))
