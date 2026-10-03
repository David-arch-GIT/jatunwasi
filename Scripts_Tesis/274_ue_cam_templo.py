import unreal
eas=unreal.EditorActorSubsystem()
cam=unreal.Vector(0, 11150, 175)
look=unreal.Rotator(0,0,90)  # mirar +Y (nave)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
