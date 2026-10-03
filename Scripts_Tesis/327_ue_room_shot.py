import unreal
eas=unreal.EditorActorSubsystem()
eas.set_selected_level_actors([])
target=None
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("APL_Comedor_1"):
        target=a; break
if target is None:
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("APL_"):
            target=a; break
if target:
    loc=target.get_actor_location()
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    # 4 candidatos alrededor; elegimos -Y (lado sala segun close-up previo) a 300cm, altura ojos
    cam=unreal.Vector(loc.x, loc.y-300, loc.z+20)
    look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
    ues.set_level_viewport_camera_info(cam, look)
    print(str([loc.x,loc.y,loc.z]))
unreal.EditorLevelLibrary.editor_invalidate_viewports()
