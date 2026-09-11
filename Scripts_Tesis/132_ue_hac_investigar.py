# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Investiga en la hacienda (-7000,-2500): (1) mallas FLANAS con colision (tapetes que
#   bloquean), (2) componentes de audio + su atenuacion y altura (para aislar el del 2do piso), (3) la rampa de
#   escalera (rotacion/slope) + colisiones cerca de las escaleras.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hac_investigar.json"
CX, CY, R = -7000.0, -2500.0, 2500.0
res = {"flat_con_colision": [], "audio": [], "escalera": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x-CX, loc.y-CY) > R:
        continue
    lbl = a.get_actor_label()
    # (1) mallas flanas con colision
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp.get_class().get_name() in ("InstancedStaticMeshComponent","HierarchicalInstancedStaticMeshComponent"):
            continue
        try:
            ce = comp.get_collision_enabled()
            if ce == unreal.CollisionEnabled.NO_COLLISION:
                continue
            org, ext = a.get_actor_bounds(False)
            # flat = Z chico, XY moderado
            if ext.z < 25 and (ext.x > 30 or ext.y > 30):
                res["flat_con_colision"].append({"label": lbl, "loc": [round(loc.x),round(loc.y),round(loc.z)], "ext": [round(ext.x),round(ext.y),round(ext.z)], "col": str(ce)})
        except Exception as e:
            res["err"].append("flat %s: %s" % (lbl, str(e)[:30]))
    # (2) audio
    for ac in a.get_components_by_class(unreal.AudioComponent):
        try:
            info = {"label": lbl, "z": round(loc.z)}
            s = ac.get_editor_property("sound")
            info["sound"] = s.get_name() if s else "?"
            att = ac.get_editor_property("attenuation_settings")
            info["att_asset"] = att.get_name() if att else "override_o_none"
            res["audio"].append(info)
        except Exception as e:
            res["err"].append("audio %s: %s" % (lbl, str(e)[:30]))
    # (3) escalera
    if "stair" in lbl.lower() or "escalera" in lbl.lower():
        try:
            rot = a.get_actor_rotation()
            org, ext = a.get_actor_bounds(False)
            res["escalera"].append({"label": lbl, "rot": [round(rot.pitch,1),round(rot.yaw,1),round(rot.roll,1)], "loc":[round(loc.x),round(loc.y),round(loc.z)], "ext":[round(ext.x),round(ext.y),round(ext.z)]})
        except Exception as e:
            res["err"].append("stair %s: %s" % (lbl, str(e)[:30]))
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("HAC INVESTIGAR flat=%d audio=%d escalera=%d" % (len(res["flat_con_colision"]), len(res["audio"]), len(res["escalera"])))
