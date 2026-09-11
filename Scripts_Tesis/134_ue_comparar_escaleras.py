# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Compara escaleras CONVENTO (funciona con joystick) vs HACIENDA (no sube). Reporta colision de cada
#   componente + si la malla tiene colision propia + rotacion. Para replicar en hacienda lo que funciona en convento.
#   Tambien re-mide la plaza (tris) para confirmar fluidez tras el horizonte.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/comparar_esc.json"
res = {"convento": [], "hacienda": [], "plaza_tris_M": None, "err": []}
eas = unreal.EditorActorSubsystem()
def stair_info(a):
    info = {"label": a.get_actor_label(), "comps": []}
    try:
        r = a.get_actor_rotation(); info["rot"] = [round(r.pitch,1),round(r.yaw,1),round(r.roll,1)]
        info["loc"] = [round(v) for v in [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z]]
    except Exception: pass
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            ce = str(comp.get_collision_enabled())
            m = comp.get_editor_property("static_mesh")
            mc = "?"
            if m:
                bs = m.get_editor_property("body_setup")
                if bs:
                    ag = bs.get_editor_property("agg_geom")
                    # contar primitivas de colision
                    try:
                        nconv = len(ag.get_editor_property("convex_elems"))
                        nbox = len(ag.get_editor_property("box_elems"))
                        mc = "conv=%d box=%d" % (nconv, nbox)
                    except Exception:
                        mc = "?"
                cct = str(m.get_editor_property("collision_complexity")) if hasattr(m,'get_editor_property') else "?"
            info["comps"].append({"col_comp": ce, "mesh_col": mc, "mesh": m.get_name() if m else "-"})
        except Exception as e:
            res["err"].append(str(e)[:40])
    return info
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label(); low = lbl.lower()
    if "stair" in low or "escalera" in low or "grada" in low:
        try:
            loc = a.get_actor_location()
            d_conv = math.hypot(loc.x-6500, loc.y-5000)
            d_hac = math.hypot(loc.x-(-7000), loc.y-(-2500))
            if d_conv < 4000:
                res["convento"].append(stair_info(a))
            elif d_hac < 4000:
                res["hacienda"].append(stair_info(a))
        except Exception as e:
            res["err"].append(str(e)[:40])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("COMPARAR conv=%d hac=%d" % (len(res["convento"]), len(res["hacienda"])))
