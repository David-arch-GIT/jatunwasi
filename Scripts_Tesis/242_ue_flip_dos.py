import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flip_dos.json"
res = {}
eas = unreal.EditorActorSubsystem()
FIX = ["MUS_Cuadro_03", "MUS_Cuadro_coc1"]
down = unreal.Vector(0,0,-1)
frames = {}; planos = {}
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    if lbl in FIX: frames[lbl] = a
    if lbl.startswith("FotoPlano_"): planos[lbl.replace("FotoPlano_","")] = a
for fn in FIX:
    fa = frames.get(fn); pl = planos.get(fn)
    if not fa or not pl: res[fn] = "falta"; continue
    o, e = fa.get_actor_bounds(False)
    yaw = math.radians(fa.get_actor_rotation().yaw)
    nx = -math.sin(yaw); ny = math.cos(yaw)
    # lado +normal (opuesto al actual)
    room = unreal.Vector(nx, ny, 0.0)
    rot = unreal.MathLibrary.make_rot_from_zy(room, down)
    pos = unreal.Vector(o.x + nx*4.0, o.y + ny*4.0, o.z)
    pl.set_actor_location_and_rotation(pos, rot, False, False)
    res[fn] = {"pos": [round(pos.x,1), round(pos.y,1), round(pos.z,1)]}
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
