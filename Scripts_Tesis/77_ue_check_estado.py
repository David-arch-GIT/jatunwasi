# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Verifica conexion MCPUnreal, reporta mapa actual, cuenta actores y lista apariciones App3D_*/Snd_App_* existentes. Escribe JSON a Saved/ClaudeBackups.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/estado_check.json"
res = {"map": None, "total": 0, "apps": [], "snds": [], "app3d_hidden": []}
try:
    res["map"] = unreal.EditorLevelLibrary.get_editor_world().get_name()
except Exception as e:
    res["map"] = "ERR:%s" % e
try:
    acts = unreal.EditorActorSubsystem().get_all_level_actors()
except Exception:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
res["total"] = len(acts)
for a in acts:
    l = a.get_actor_label()
    if l.startswith("App3D_"):
        loc = a.get_actor_location()
        res["apps"].append({"label": l, "cls": a.get_class().get_name(),
                            "loc": [round(loc.x), round(loc.y), round(loc.z)],
                            "hidden": a.is_hidden_ed()})
    elif l.startswith("Snd_App"):
        res["snds"].append(l)
    elif "Apparition" in l or "App_" in l:
        res["app3d_hidden"].append(l)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ESTADO CHECK OK map=%s total=%d apps=%d" % (res["map"], res["total"], len(res["apps"])))
