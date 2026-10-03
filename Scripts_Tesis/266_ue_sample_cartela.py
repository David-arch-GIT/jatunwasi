import unreal, json, math
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/sample_cartela.json"
res={}
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
plane=EAL.load_asset("/Engine/BasicShapes/Plane")
mi=EAL.load_asset("/Game/Cartelas/Tex/MI_Cart_varon_valluno")
man=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="HF_ManiquiM_G": man=a; break
o,e=man.get_actor_bounds(False)
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label()=="Cartela_SAMPLE": eas.destroy_actor(a)
# cartela mirando -X (hacia la sala), al costado izquierdo de la vitrina
normal=unreal.Vector(-1,0,0)
rot=unreal.MathLibrary.make_rot_from_zy(normal, unreal.Vector(0,0,-1))
pos=unreal.Vector(o.x-55, o.y, o.z+35)
pl=eas.spawn_actor_from_object(plane, pos, rot)
pl.set_actor_label("Cartela_SAMPLE")
pl.set_actor_scale3d(unreal.Vector(0.95, 0.60, 1.0))
smc=pl.get_component_by_class(unreal.StaticMeshComponent)
smc.set_material(0, mi); smc.set_cast_shadow(False)
res["pos"]=[round(pos.x,1),round(pos.y,1),round(pos.z,1)]
cam=unreal.Vector(pos.x-135, pos.y, pos.z+3)
look=unreal.MathLibrary.find_look_at_rotation(cam, pos)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
open(OUT,"w").write(json.dumps(res, indent=1))
