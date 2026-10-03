import unreal
eas=unreal.EditorActorSubsystem()
act=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="Cartela_san_sebastian": act=a; break
panel=None
for c in act.get_components_by_class(unreal.StaticMeshComponent): panel=c
loc=panel.get_world_location(); rot=panel.get_world_rotation()
zdir=unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(0,0,1))
cam=unreal.Vector(loc.x+zdir.x*135, loc.y+zdir.y*135, loc.z+zdir.z*135+3)
look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
