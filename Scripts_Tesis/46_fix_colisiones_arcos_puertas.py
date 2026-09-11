# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: Pone la colision de las mallas de arcos y puertas (Arch_Bay, Wall_Door) en "Complex As Simple" para que respeten el hueco real, sin tocar la geometria visual. Luego reconstruye el NavMesh.
# Por que se necesito: El usuario no puede atravesar los arcos del Convento; la colision simple tapaba el vano.
# Resultado obtenido: (pendiente) mallas ajustadas + NavMesh reconstruido.
# ------------------------------------------------------------

import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_colisiones.json"
TARGETS = {"SM_HACKIT_Arch_Bay", "SM_HACKIT_Wall_Door"}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

# 1) Recolectar las mallas asset unicas objetivo
meshes = {}
for a in all_actors():
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            sm = comp.get_editor_property("static_mesh")
        except Exception:
            sm = None
        if sm and sm.get_name() in TARGETS:
            meshes[sm.get_name()] = sm

res = {"cambiadas": [], "no_encontradas": list(TARGETS - set(meshes.keys()))}

# 2) Poner Complex As Simple en cada asset y guardar
for nm, sm in meshes.items():
    try:
        bs = sm.get_editor_property("body_setup")
        antes = str(bs.get_editor_property("collision_trace_flag"))
        bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(sm)
        despues = str(bs.get_editor_property("collision_trace_flag"))
        res["cambiadas"].append({"mesh": nm, "antes": antes, "despues": despues})
    except Exception as e:
        res["cambiadas"].append({"mesh": nm, "error": str(e)})

# 3) Reconstruir NavMesh
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    res["navmesh"] = "RebuildNavigation lanzado"
except Exception as e:
    res["navmesh"] = "error: " + str(e)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("FIX colisiones: cambiadas=%d" % len(res["cambiadas"]))
