import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/doscara.json"
res = {}
EAL = unreal.EditorAssetLibrary
# 1) material dos caras
mat = EAL.load_asset("/Game/FotosAntano/M_FotoPlane")
mat.set_editor_property("two_sided", True)
unreal.MaterialEditingLibrary.recompile_material(mat)
EAL.save_asset("/Game/FotosAntano/M_FotoPlane", only_if_is_dirty=False)
# 2) mover los 2 planos al centro del lienzo (sin offset)
eas = unreal.EditorActorSubsystem()
FIX = ["MUS_Cuadro_03","MUS_Cuadro_coc1"]
frames={}; planos={}
for a in eas.get_all_level_actors():
    l=a.get_actor_label()
    if l in FIX: frames[l]=a
    if l.startswith("FotoPlano_"): planos[l.replace("FotoPlano_","")]=a
down=unreal.Vector(0,0,-1)
for fn in FIX:
    fa=frames[fn]; pl=planos.get(fn)
    o,e=fa.get_actor_bounds(False)
    yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
    room=unreal.Vector(nx,ny,0.0)
    rot=unreal.MathLibrary.make_rot_from_zy(room, down)
    pl.set_actor_location_and_rotation(unreal.Vector(o.x,o.y,o.z), rot, False, False)
    res[fn]=[round(o.x,1),round(o.y,1),round(o.z,1)]
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
