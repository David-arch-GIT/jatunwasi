# Deselecciona todo y encuadra de cerca un farol de pared concreto para foto limpia.
import unreal
eas=unreal.EditorActorSubsystem()
eas.set_selected_level_actors([])  # quitar cajas de seleccion
target=None
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("APL_Zaguan_1") or a.get_actor_label().startswith("APL_Comedor_1"):
        target=a; break
if target is None:
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm=c.get_editor_property("static_mesh")
            if sm and sm.get_name()=="SM_JW_WallLantern":
                target=a; break
        if target: break
if target:
    loc=target.get_actor_location()
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    # probar 4 posiciones alrededor a 90cm y elegir la de camara; usamos +X/-Y frontal tipico
    cam=unreal.Vector(loc.x+70, loc.y-70, loc.z+10)
    look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
    ues.set_level_viewport_camera_info(cam, look)
    print(str([loc.x,loc.y,loc.z]))
unreal.EditorLevelLibrary.editor_invalidate_viewports()
