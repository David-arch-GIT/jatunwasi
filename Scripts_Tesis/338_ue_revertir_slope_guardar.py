# Revierte pendiente del NavMesh a 44 (estado conocido) para no shipear cambio no verificado. Guarda nivel.
import unreal
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if "RecastNavMesh" in a.get_class().get_name():
        try: a.set_editor_property("agent_max_slope", 44.0)
        except Exception: pass
        break
unreal.EditorLoadingAndSavingUtils.save_current_level()
print("revertido y guardado")
