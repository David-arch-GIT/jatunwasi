import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/coc1.json"
eas = unreal.EditorActorSubsystem()
fa=None; pl=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="MUS_Cuadro_coc1": fa=a
    if a.get_actor_label()=="FotoPlano_MUS_Cuadro_coc1": pl=a
o,e=fa.get_actor_bounds(False)
yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
room=unreal.Vector(nx,ny,0.0)  # +normal
rot=unreal.MathLibrary.make_rot_from_zy(room, unreal.Vector(0,0,-1))
pos=unreal.Vector(o.x+nx*6.0, o.y+ny*6.0, o.z)
pl.set_actor_location_and_rotation(pos, rot, False, False)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps({"pos":[round(pos.x,1),round(pos.y,1),round(pos.z,1)]}))
