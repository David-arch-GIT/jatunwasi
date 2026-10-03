import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/proyeccion_nav.json"
res = {"criaturas": [], "reubicadas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
HH = 88.0
def project(x, y, z):
    for ext in [unreal.Vector(200,200,300), unreal.Vector(600,600,600), unreal.Vector(1500,1500,1000)]:
        try:
            r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x,y,z), None, None, ext)
            if r is not None:
                # puede venir como (bool, Vector) o Vector
                if isinstance(r, tuple):
                    if r[0]: return r[1]
                else:
                    return r
        except Exception as e:
            res["err"].append("proj:" + str(e)[:40]); return None
    return None
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("Cria_"): continue
    loc = a.get_actor_location()
    feet_z = loc.z - HH
    pj = project(loc.x, loc.y, feet_z)
    info = {"lab": lab, "actual_feet": [round(loc.x), round(loc.y), round(feet_z)]}
    if pj is not None:
        dx = pj.x - loc.x; dy = pj.y - loc.y; dz = pj.z - feet_z
        dist = (dx*dx + dy*dy)**0.5
        info["nav_point"] = [round(pj.x), round(pj.y), round(pj.z)]
        info["delta_horizontal"] = round(dist)
        info["delta_z"] = round(dz)
        # reubicar si el desplazamiento horizontal es razonable (<700) y hay cambio necesario
        if dist < 700:
            a.set_actor_location(unreal.Vector(pj.x, pj.y, pj.z + HH), False, True)
            res["reubicadas"].append(lab + " -> nav (dh=%d dz=%d)" % (round(dist), round(dz)))
        else:
            info["nota"] = "navmesh lejos, NO reubicado auto"
    else:
        info["nav_point"] = "SIN NAVMESH CERCA"
    res["criaturas"].append(info)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
