import unreal
eas=unreal.EditorActorSubsystem()
fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="APL_Comedor_1": fa=a; break
loc=fa.get_actor_location()
cam=unreal.Vector(loc.x-420, loc.y, loc.z-40)
look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
