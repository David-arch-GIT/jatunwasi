import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fixqc.json"
res={}
eas=unreal.EditorActorSubsystem()
down=unreal.Vector(0,0,-1)
byl={}
for a in eas.get_all_level_actors(): byl[a.get_actor_label()]=a
# quena -> +Y
q=byl.get("HF_Quena_G"); pq=byl.get("Cartela_quena")
if q and pq:
    w=q.get_actor_location()
    normal=unreal.Vector(0,1,0)
    rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
    pos=unreal.Vector(w.x, w.y+50, 150.0)
    pq.set_actor_location_and_rotation(pos, rot, False, False)
    res["quena"]=[round(pos.x,1),round(pos.y,1),round(pos.z,1)]
# catre: usar bounds origin del actor + mirar la escena
catre=byl.get("CV2_Catre"); pc=byl.get("Cartela_catre")
if catre and pc:
    o,e=catre.get_actor_bounds(False)
    res["catre_bounds_o"]=[round(o.x,1),round(o.y,1),round(o.z,1)]
    res["catre_bounds_e"]=[round(e.x,1),round(e.y,1),round(e.z,1)]
    # ubicar la cartela cerca del origen de bounds, mirando -Y
    normal=unreal.Vector(0,1,0)
    rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
    pos=unreal.Vector(o.x, o.y+60, 150.0)
    pc.set_actor_location_and_rotation(pos, rot, False, False)
    res["catre"]=[round(pos.x,1),round(pos.y,1),round(pos.z,1)]
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
