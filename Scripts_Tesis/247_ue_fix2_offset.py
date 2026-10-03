import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix2.json"
res = {}
eas = unreal.EditorActorSubsystem()
FIX = ["MUS_Cuadro_03","MUS_Cuadro_coc1"]
frames={}; planos={}
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l in FIX: frames[l]=a
    if l.startswith("FotoPlano_"): planos[l.replace("FotoPlano_","")]=a
down=unreal.Vector(0,0,-1)
for fn in FIX:
    fa=frames[fn]; pl=planos[fn]
    o,e=fa.get_actor_bounds(False)
    yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
    room=unreal.Vector(nx,ny,0.0)  # +normal = sala
    rot=unreal.MathLibrary.make_rot_from_zy(room, down)
    pos=unreal.Vector(o.x+nx*6.0, o.y+ny*6.0, o.z)
    pl.set_actor_location_and_rotation(pos, rot, False, False)
    res[fn]=[round(pos.x,1),round(pos.y,1),round(pos.z,1)]
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
