# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) (1) Estado REAL de colision de cada componente de la escalera y la rampa. (2) Localiza senderos/caminos
#   cerca de la hacienda y su altura vs el piso, para hallar la brecha de la entrada.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/loc_sendero.json"
res = {"escalera_comps": [], "rampa_comps": [], "senderos_cerca_hac": [], "err": []}
eas = unreal.EditorActorSubsystem()
HAC = (-7000, -2500)
def comps(a):
    out = []
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            tf = "?"
            if m:
                bs = m.get_editor_property("body_setup")
                if bs: tf = str(bs.get_editor_property("collision_trace_flag")).split(".")[-1]
            out.append({"col": str(c.get_collision_enabled()).split(".")[-1], "trace": tf, "mesh": m.get_name() if m else "-"})
        except Exception as e:
            res["err"].append(str(e)[:40])
    return out
for a in eas.get_all_level_actors():
    l = a.get_actor_label(); low = l.lower()
    if l == "HACV7_EXP_Staircase":
        res["escalera_comps"] = comps(a)
    elif l == "COL_HACV7_StairRamp":
        res["rampa_comps"] = comps(a)
    # senderos/caminos cerca de la hacienda
    if any(k in low for k in ["sendero","camino","path","trail","road","walkway"]):
        loc = a.get_actor_location()
        d = math.hypot(loc.x-HAC[0], loc.y-HAC[1])
        if d < 3000:
            o, e = a.get_actor_bounds(False)
            ce = "-"
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                try: ce = str(c.get_collision_enabled()).split(".")[-1]
                except Exception: pass
            res["senderos_cerca_hac"].append({"label": l, "d": round(d),
                "loc":[round(loc.x),round(loc.y),round(loc.z)],
                "z":[round(o.z-e.z),round(o.z+e.z)], "x":[round(o.x-e.x),round(o.x+e.x)],
                "y":[round(o.y-e.y),round(o.y+e.y)], "col": ce})
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("LOC SENDERO ok")
