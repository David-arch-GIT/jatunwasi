# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) EVALUACION LIGERA (solo AssetRegistry, NO carga texturas) para el crash al re-colocar visor:
#   estima memoria de texturas por tags (Dimensions), lista las mas pesadas, cuenta assets por tipo,
#   y revisa setup VR (GameMode, reflection captures, skeletal/audio en el mapa). No modifica nada.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/eval_mem_vr.json"
res = {"tex_total_MB_est": 0.0, "tex_count": 0, "tex_over_2k": 0, "top_tex": [],
       "counts": {}, "map_skeletal": 0, "map_audio": 0, "map_reflcap": 0, "map_particles": 0}
ar = unreal.AssetRegistryHelpers.get_asset_registry()

def bpp_for(fmt):
    f = str(fmt)
    if "DXT1" in f or "BC1" in f or "BC4" in f: return 0.5
    if "DXT5" in f or "BC3" in f or "BC5" in f or "BC7" in f or "ASTC" in f: return 1.0
    if "RGBA8" in f or "BGRA8" in f or "B8G8R8A8" in f: return 4.0
    if "FloatRGBA" in f: return 8.0
    return 1.0  # asumir comprimido

# --- Texturas via AssetRegistry (sin cargar) ---
tex = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
big = []
for d in tex:
    p = str(d.package_name)
    if not p.startswith("/Game/"):
        continue
    res["tex_count"] += 1
    dim = d.get_tag_value("Dimensions")   # ej "1024x1024" o "1024x1024x1"
    fmt = d.get_tag_value("Format") or d.get_tag_value("PixelFormat") or ""
    w = h = 0
    if dim:
        try:
            parts = str(dim).replace("X", "x").split("x")
            w = int(parts[0]); h = int(parts[1])
        except Exception:
            pass
    if w and h:
        mb = (w * h * bpp_for(fmt) * 1.333) / (1024.0 * 1024.0)
        res["tex_total_MB_est"] += mb
        if max(w, h) > 2048:
            res["tex_over_2k"] += 1
        big.append((round(mb, 2), "%dx%d" % (w, h), str(d.asset_name)))
big.sort(key=lambda t: -t[0])
res["top_tex"] = big[:25]
res["tex_total_MB_est"] = round(res["tex_total_MB_est"], 1)

# --- Conteo por tipo (ligero) ---
for cls in ["StaticMesh", "SkeletalMesh", "Material", "MaterialInstanceConstant", "SoundWave", "Texture2D", "AnimSequence"]:
    n = len(ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", cls), True))
    res["counts"][cls] = n

# --- Setup VR en el mapa actual ---
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_components_by_class(unreal.SkeletalMeshComponent):
        res["map_skeletal"] += 1
    if a.get_components_by_class(unreal.AudioComponent):
        res["map_audio"] += 1
    cn = a.get_class().get_name()
    if "ReflectionCapture" in cn:
        res["map_reflcap"] += 1
    if a.get_components_by_class(unreal.ParticleSystemComponent) or a.get_components_by_class(unreal.NiagaraComponent):
        res["map_particles"] += 1

open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("EVAL tex_est=%.1fMB count=%d over2k=%d" % (res["tex_total_MB_est"], res["tex_count"], res["tex_over_2k"]))
