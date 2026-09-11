# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) SOLO LECTURA. Reporta el/los PlayerStart y su ubicacion, + landmarks de zonas que funcionan
#   (convento/templo/hacienda/caminos) con su ubicacion, para elegir un punto de inicio FUERA de la plaza.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/spawn_info.json"
res = {"player_starts": [], "landmarks": {}}
eas = unreal.EditorActorSubsystem()
PCX, PCY = 0.0, -1000.0
want = ["convento", "templo", "iglesia", "hacienda", "path", "sendero", "camino", "mirador"]
found = {k: None for k in want}
for a in eas.get_all_level_actors():
    cls = a.get_class().get_name()
    lbl = a.get_actor_label()
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if cls == "PlayerStart" or "PlayerStart" in lbl:
        d = math.hypot(loc.x - PCX, loc.y - PCY)
        res["player_starts"].append({"label": lbl, "x": round(loc.x), "y": round(loc.y), "z": round(loc.z), "dist_plaza_m": round(d/100.0,1)})
    low = lbl.lower()
    for k in want:
        if k in low and found[k] is None:
            d = math.hypot(loc.x - PCX, loc.y - PCY)
            found[k] = {"label": lbl, "x": round(loc.x), "y": round(loc.y), "z": round(loc.z), "dist_plaza_m": round(d/100.0,1)}
res["landmarks"] = {k: v for k, v in found.items() if v}
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("SPAWN INFO starts=%d landmarks=%d" % (len(res["player_starts"]), len(res["landmarks"])))
