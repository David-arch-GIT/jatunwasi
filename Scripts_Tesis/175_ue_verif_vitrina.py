# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Verifica los actores VIT_Habito_* colocados: ubicacion, bounds (alto real), y si hay algo tapandolos.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_vitrina.json"
res = {"actores": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("VIT_Habito"):
        continue
    loc = a.get_actor_location()
    org, ext = a.get_actor_bounds(False)
    res["actores"].append({
        "label": lab,
        "loc": [round(loc.x), round(loc.y), round(loc.z)],
        "centro_bounds": [round(org.x), round(org.y), round(org.z)],
        "alto_cm": round(ext.z * 2),
        "ancho_cm": round(ext.x * 2),
        "prof_cm": round(ext.y * 2),
        "scale": [round(a.get_actor_scale3d().x, 1), round(a.get_actor_scale3d().y, 1), round(a.get_actor_scale3d().z, 1)]
    })
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("VERIF VITRINA n=%d" % len(res["actores"]))
