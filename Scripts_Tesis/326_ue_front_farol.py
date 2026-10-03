import unreal
eas=unreal.EditorActorSubsystem()
eas.set_selected_level_actors([])
target=None
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("APL_Comedor_1") or a.get_actor_label().startswith("APL_Zaguan_1"):
        target=a; break
if target:
    loc=target.get_actor_location()
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    # frente opuesto y un poco por debajo, mirando hacia arriba al vidrio
    cam=unreal.Vector(loc.x-60, loc.y+90, loc.z-20)
    look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(loc.x, loc.y, loc.z+10))
    ues.set_level_viewport_camera_info(cam, look)
unreal.EditorLevelLibrary.editor_invalidate_viewports()
