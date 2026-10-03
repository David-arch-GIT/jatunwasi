import unreal
eas=unreal.EditorActorSubsystem()
cam=unreal.Vector(2422+350, 2749+350, 380)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(2422,2749,150))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
