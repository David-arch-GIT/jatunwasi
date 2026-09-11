# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) AUDITORIA LIGERA de memoria de texturas (NO carga texturas = usa AssetRegistry tag Dimensions, seguro,
#   no cuelga la PC). Lista texturas >=2048 en /Game con su tamano y estima MB (ancho*alto*4/1MB, sin mips). Clasifica
#   en SEGURAS de recortar (mundo/roca/corteza/piso/hoja/impostor/cerca) vs HERO (santo/museo/retrato/piel/tela) que NO
#   se tocan. Solo mide, escribe JSON con listas + totales. Para decidir el recorte 2048->1024 dirigido.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/tex_mem_audit.json"
res = {"total_tex": 0, "ge2048": 0, "mb_ge2048": 0.0, "seguras": [], "hero": [], "otras": [], "err": []}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
SAFE = ["ground","terrain","rock","cliff","stone","bark","tree","trunk","leaf","foliage","grass","fern",
        "impostor","fence","cobble","dirt","moss","wood","roof","wall","floor","brick","plaster","soil","gravel"]
HERO = ["santo","saint","virgen","museo","museum","retrato","portrait","skin","piel","face","cara","cloth","tela",
        "vestiment","fabric","duende","karisiri","condenado","apparition"]
tex = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
res["total_tex"] = len(tex)
for a in tex:
    pkg = str(a.package_name)
    if not pkg.startswith("/Game"):
        continue
    nm = str(a.asset_name); low = nm.lower()
    dim = a.get_tag_value("Dimensions"); w = 0; h = 0
    if dim:
        try:
            parts = str(dim).lower().replace(" ", "").split("x")
            w = int(parts[0]); h = int(parts[1]) if len(parts) > 1 else w
        except Exception:
            pass
    if w < 2048:
        continue
    res["ge2048"] += 1
    mb = (w * h * 4) / (1024.0 * 1024.0)
    res["mb_ge2048"] += mb
    entry = [nm[:34], w, round(mb, 1)]
    if any(k in low for k in HERO):
        res["hero"].append(entry)
    elif any(k in low for k in SAFE):
        res["seguras"].append(entry)
    else:
        res["otras"].append(entry)
res["mb_ge2048"] = round(res["mb_ge2048"], 1)
res["seguras"] = sorted(res["seguras"], key=lambda e: -e[2])
res["otras"] = sorted(res["otras"], key=lambda e: -e[2])
res["n_seguras"] = len(res["seguras"]); res["n_hero"] = len(res["hero"]); res["n_otras"] = len(res["otras"])
res["mb_seguras"] = round(sum(e[2] for e in res["seguras"]), 1)
res["mb_otras"] = round(sum(e[2] for e in res["otras"]), 1)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("TEX AUDIT ge2048=%d mb=%.0f seguras=%d" % (res["ge2048"], res["mb_ge2048"], len(res["seguras"])))
