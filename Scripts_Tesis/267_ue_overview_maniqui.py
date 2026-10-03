import unreal, math
eas=unreal.EditorActorSubsystem()
man=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="HF_ManiquiM_G": man=a; break
o,e=man.get_actor_bounds(False)
# camara alta y atras en diagonal, mirando el maniqui
cam=unreal.Vector(o.x+260, o.y+260, o.z+180)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(o.x,o.y,o.z))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
