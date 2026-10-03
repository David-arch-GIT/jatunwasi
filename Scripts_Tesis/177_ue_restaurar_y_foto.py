# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Restaura la vitrina (unhide), reposiciona la luz al frente-arriba del habito (mejor realce), fija
#   camara 3/4 frontal y toma HighResShot (render fresco a Saved/Screenshots, evita el capture_viewport stale).
# ------------------------------------------------------------
import unreal
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab == "VIT_Habito_Vitrina":
        a.set_actor_hidden_in_game(False)
        a.set_is_temporarily_hidden_in_editor(False)
    if lab == "VIT_Habito_Luz":
        a.set_actor_location(unreal.Vector(6120.0, 3760.0, 235.0), False, False)  # frente(+y)-arriba
        lc = a.get_component_by_class(unreal.PointLightComponent)
        lc.set_intensity(12.0)
        lc.set_attenuation_radius(260.0)
els = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
els.set_level_viewport_camera_info(unreal.Vector(6560.0, 4230.0, 175.0), unreal.Rotator(0.0, -5.0, 235.0))
unreal.SystemLibrary.execute_console_command(w, "HighResShot 1280x720")
unreal.log("FOTO tomada")
