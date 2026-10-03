# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Busca AnimSequences en /Game (walk/idle/etc) y sus esqueletos; skeletons de karisiri_full/condenado_full/
#   duende_full; y si hay AnimBlueprints o LevelSequences (LS_Apariciones) que los muevan. Para saber si los rigs
#   tienen animaciones utilizables. Solo lee.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_anims.json"
res = {"anim_sequences": [], "anim_blueprints": [], "level_sequences": [], "skel_meshes": [], "err": []}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
def names(cls):
    out = []
    try:
        for a in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", cls), True):
            pkg = str(a.package_name)
            if pkg.startswith("/Game"):
                out.append(pkg)
    except Exception as e:
        res["err"].append(cls + ":" + str(e)[:30])
    return out
# AnimSequences
for p in names("AnimSequence"):
    res["anim_sequences"].append(p.split("/")[-1] + "  @ " + "/".join(p.split("/")[:-1])[-40:])
# AnimBlueprints (clase AnimBlueprint esta en Engine? es un Blueprint generated). Buscar por nombre
allbp = names("AnimBlueprint")
for p in allbp:
    res["anim_blueprints"].append(p.split("/")[-1])
# LevelSequences
for p in names("LevelSequence"):
    res["level_sequences"].append(p.split("/")[-1])
# Skeletal meshes de las criaturas
for p in names("SkeletalMesh"):
    nm = p.split("/")[-1].lower()
    if any(k in nm for k in ["karisiri", "condenado", "duende"]):
        m = unreal.EditorAssetLibrary.load_asset(p)
        d = {"mesh": p.split("/")[-1]}
        try:
            sk = m.get_editor_property("skeleton")
            d["skeleton"] = sk.get_name() if sk else "NINGUNO"
        except Exception as e:
            d["err"] = str(e)[:30]
        try:
            d["tris_render"] = "SK (ver LOD)"
        except Exception: pass
        res["skel_meshes"].append(d)
res["n_anims"] = len(res["anim_sequences"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG ANIMS anims=%d abp=%d ls=%d" % (len(res["anim_sequences"]), len(res["anim_blueprints"]), len(res["level_sequences"])))
