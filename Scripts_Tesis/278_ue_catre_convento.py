import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/catrefix.json"
eas=unreal.EditorActorSubsystem()
down=unreal.Vector(0,0,-1)
pc=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="Cartela_catre": pc=a; break
# ubicar en el convento, junto al habito, mirando +Y (como el habito)
normal=unreal.Vector(0,1,0)
rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
pos=unreal.Vector(7720, 4315, 150.0)
pc.set_actor_location_and_rotation(pos, rot, False, False)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps({"catre":[pos.x,pos.y,pos.z]}))
