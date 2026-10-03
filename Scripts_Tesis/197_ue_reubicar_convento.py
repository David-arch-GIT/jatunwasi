import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reubicar_conv.json"
res = {"movidas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
HH = 88.0
def suelo(x, y):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,400), unreal.Vector(x,y,-200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]: return float(t[5].z), (t[9].get_actor_label()[:16] if t[9] else "?")
    return 0.0, "VACIO"
# spots convento verificados (open floor)
DEST = {"Cria_Karisiri": (5890.0, 4810.0), "Cria_Condenado": (6510.0, 5390.0)}
NAVDEST = {"Nav_Cria_Karisiri": (5890.0, 4810.0), "Nav_Cria_Condenado": (6510.0, 5390.0)}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in DEST:
        x, y = DEST[lab]; gz, floor = suelo(x, y)
        a.set_actor_location(unreal.Vector(x, y, gz + HH), False, True)
        res["movidas"].append({"lab": lab, "xy": [round(x), round(y)], "feet_z": round(gz), "piso": floor})
    if lab in NAVDEST:
        x, y = NAVDEST[lab]
        a.set_actor_location(unreal.Vector(x, y, 100.0), False, True)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
open(OUT, "w").write(json.dumps(res, indent=1))
