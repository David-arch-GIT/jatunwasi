import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/planta_baja.json"
res = {"movidas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
HH = 88.0
def suelo_bajo(x, y):
    # trazar desde z200 (bajo el piso superior a 362) para caer a planta baja
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,200), unreal.Vector(x,y,-200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]: return float(t[5].z), (t[9].get_actor_label()[:18] if t[9] else "?")
    return 0.0, "VACIO"
DEST = {"Cria_Karisiri": (5890.0, 4810.0), "Cria_Condenado": (6510.0, 5390.0)}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in DEST:
        x, y = DEST[lab]; gz, floor = suelo_bajo(x, y)
        a.set_actor_location(unreal.Vector(x, y, gz + HH), False, True)
        res["movidas"].append({"lab": lab, "xy": [round(x), round(y)], "feet_z": round(gz), "piso": floor})
    if lab == "Nav_Cria_Karisiri":
        a.set_actor_location(unreal.Vector(5890.0, 4810.0, 80.0), False, True)
        a.set_actor_scale3d(unreal.Vector(12.0, 12.0, 4.0))  # mas plano, solo planta baja
    if lab == "Nav_Cria_Condenado":
        a.set_actor_location(unreal.Vector(6510.0, 5390.0, 80.0), False, True)
        a.set_actor_scale3d(unreal.Vector(12.0, 12.0, 4.0))
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
open(OUT, "w").write(json.dumps(res, indent=1))
