import unreal, math
eas=unreal.EditorActorSubsystem()
pl=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="FotoPlano_MUS_Cuadro_coc1": pl=a
loc=pl.get_actor_location(); rot=pl.get_actor_rotation()
zdir=unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(0,0,1))
# camara del lado -zdir (opuesto), a 120, elevada
cam=unreal.Vector(loc.x - zdir.x*120, loc.y - zdir.y*120, loc.z + 20)
look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
