import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
# nudge camera slightly then set final to force recompute
ues.set_level_viewport_camera_info(unreal.Vector(10.0, -1010.0, 4300.0), unreal.Rotator(0.0, -90.0, 0.0))
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.editor_invalidate_viewports()
except Exception as e:
    unreal.log("inval err %s" % e)
try:
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception:
    pass
ues.set_level_viewport_camera_info(unreal.Vector(0.0, -1000.0, 4200.0), unreal.Rotator(0.0, -90.0, 0.0))
unreal.log("REDRAW_DONE")
