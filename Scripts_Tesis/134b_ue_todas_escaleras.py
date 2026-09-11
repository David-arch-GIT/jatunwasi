# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Lista TODAS las escaleras/rampas/gradas del mapa con ubicacion, rotacion y colision de componente,
#   para identificar la del convento (funciona) vs hacienda (no) y replicar.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/todas_esc.json"
res = {"items": [], "err": []}
eas = unreal.EditorActorSubsystem()
KW = ["stair","escalera","grada","ramp","rampa","step","peldan","gradas"]
for a in eas.get_all_level_actors():
    low = a.get_actor_label().lower()
    if not any(k in low for k in KW):
        continue
    try:
        loc = a.get_actor_location(); r = a.get_actor_rotation()
        item = {"label": a.get_actor_label(), "loc": [round(loc.x),round(loc.y),round(loc.z)],
                "rot": [round(r.pitch,1),round(r.yaw,1),round(r.roll,1)], "cols": []}
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                ce = str(comp.get_collision_enabled()).split(".")[-1]
                m = comp.get_editor_property("static_mesh")
                has_col = False
                if m:
                    bs = m.get_editor_property("body_setup")
                    has_col = bool(bs)
                item["cols"].append({"comp_col": ce, "mesh_has_bodysetup": has_col, "mesh": m.get_name() if m else "-"})
            except Exception as e:
                res["err"].append(str(e)[:30])
        res["items"].append(item)
    except Exception as e:
        res["err"].append(str(e)[:30])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("TODAS ESC %d" % len(res["items"]))
