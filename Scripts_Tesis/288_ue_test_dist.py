import unreal
DIST=float(__import__("sys").argv[0]) if False else 900.0
eas=unreal.EditorActorSubsystem()
act=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="Cartela_san_sebastian": act=a; break
panel=None
for c in act.get_components_by_class(unreal.StaticMeshComponent): panel=c
loc=panel.get_world_location(); rot=panel.get_world_rotation()
zdir=unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(0,0,1))
d=__DIST__
cam=unreal.Vector(loc.x+zdir.x*d, loc.y+zdir.y*d, loc.z+zdir.z*d+40)
look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
