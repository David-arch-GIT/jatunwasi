# NavMesh a ESTATICO (horneado) para que viaje listo en el APK sin depender de generarse en runtime.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_static.json"
res={}
eas=unreal.EditorActorSubsystem()
world=unreal.EditorLevelLibrary.get_editor_world()
rec=None
for a in eas.get_all_level_actors():
    if "RecastNavMesh" in a.get_class().get_name():
        rec=a; break
if rec:
    res["antes"]=str(rec.get_editor_property("runtime_generation"))
    # STATIC = 0
    rec.set_editor_property("runtime_generation", unreal.RuntimeGenerationType.STATIC)
    res["ahora"]=str(rec.get_editor_property("runtime_generation"))
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    res["rebuild"]="lanzado"
else:
    res["err"]="no recast"
open(OUT,"w").write(json.dumps(res,indent=1))
