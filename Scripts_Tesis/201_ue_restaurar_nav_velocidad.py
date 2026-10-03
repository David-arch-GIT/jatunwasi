import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/restaurar_nav.json"
res = {"nav": [], "vel": [], "err": []}
eas = unreal.EditorActorSubsystem()
ell = unreal.EditorLevelLibrary
w = ell.get_editor_world()
# re-crear navmesh grande (convento + hacienda) para que naveguen bien
NAV = {
    "CONV_NavBounds2": ((6200.0, 5100.0, 200.0), (48.0, 48.0, 12.0)),   # ~4800x4800
    "HAC_NavBounds2": ((-7050.0, -1800.0, 200.0), (46.0, 48.0, 12.0)),
}
existing = set(a.get_actor_label() for a in eas.get_all_level_actors())
for lab, ((x,y,z),(sx,sy,sz)) in NAV.items():
    if lab in existing: continue
    try:
        v = ell.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(x,y,z))
        v.set_actor_label(lab); v.set_actor_scale3d(unreal.Vector(sx,sy,sz))
        res["nav"].append(lab)
    except Exception as e: res["err"].append("nav "+lab+":"+str(e)[:30])
# velocidad sensata en las 3 instancias (por si el grafo no la fija)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("Cria_"):
        cm = a.get_component_by_class(unreal.CharacterMovementComponent)
        if cm:
            cm.set_editor_property("max_walk_speed", 90.0)
            cm.set_editor_property("max_acceleration", 300.0)
            cm.set_editor_property("braking_deceleration_walking", 500.0)
            res["vel"].append(a.get_actor_label()+" speed90")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
open(OUT, "w").write(json.dumps(res, indent=1))
