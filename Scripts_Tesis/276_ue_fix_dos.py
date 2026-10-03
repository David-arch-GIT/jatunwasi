import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fixdos.json"
res={}
eas=unreal.EditorActorSubsystem()
down=unreal.Vector(0,0,-1)
byl={}
for a in eas.get_all_level_actors(): byl[a.get_actor_label()]=a
# obj origins
FIX={
 "pollera_cochabambina":("HF_ManiquiF_G",(0,1),82),
 "habito":("VIT_Habito_Mesh",(0,1),66),
}
for cart,(objlbl,(nx,ny),off) in FIX.items():
    obj=byl.get(objlbl); pl=byl.get("Cartela_"+cart)
    if not obj or not pl: res[cart]="falta"; continue
    o,e=obj.get_actor_bounds(False)
    normal=unreal.Vector(nx,ny,0)
    rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
    pos=unreal.Vector(o.x+nx*off, o.y+ny*off, 150.0)
    pl.set_actor_location_and_rotation(pos, rot, False, False)
    res[cart]=[round(pos.x,1),round(pos.y,1),round(pos.z,1)]
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
