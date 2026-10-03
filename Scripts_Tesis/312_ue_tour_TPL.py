import unreal
cx,cy,cz=__CAM__
tx,ty,tz=__TGT__
eas=unreal.EditorActorSubsystem()
cam=unreal.Vector(cx,cy,cz)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(tx,ty,tz))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
