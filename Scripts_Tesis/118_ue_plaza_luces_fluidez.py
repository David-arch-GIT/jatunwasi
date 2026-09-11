# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Sube la fluidez de la plaza reduciendo las luces dinamicas (16 -> ~8, el mayor costo mobile).
#   Mantiene las 8 mas cercanas al centro (donde miras de cerca); apaga las demas (sus faroles siguen brillando por
#   emisivo). NO sube skylight (evita el look plano). Solo luces de la plaza (LP_/LC_Farol/PLZ), no toca hacienda/otras.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_luces.json"
CX, CY, R = 0.0, -1000.0, 4500.0
KEEP = 8
res = {"encontradas": 0, "mantenidas": 0, "apagadas": 0, "apagadas_lbl": [], "err": []}
eas = unreal.EditorActorSubsystem()
cand = []
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    low = lbl.lower()
    if not (low.startswith("lp_") or "farol" in low or low.startswith("plz")):
        continue
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    d = math.hypot(loc.x - CX, loc.y - CY)
    if d > R:
        continue
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent", "SpotLightComponent"):
            cand.append((d, lc, lbl))
cand.sort(key=lambda t: t[0])
res["encontradas"] = len(cand)
for i, (d, lc, lbl) in enumerate(cand):
    try:
        if i < KEEP:
            lc.set_visibility(True, False)
            lc.set_editor_property("cast_shadows", False)
            res["mantenidas"] += 1
        else:
            lc.set_visibility(False, False)
            res["apagadas"] += 1
            res["apagadas_lbl"].append(lbl)
    except Exception as e:
        res["err"].append("%s: %s" % (lbl, str(e)[:50]))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA LUCES enc=%d keep=%d off=%d" % (res["encontradas"], res["mantenidas"], res["apagadas"]))
