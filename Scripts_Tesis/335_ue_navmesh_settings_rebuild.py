# Lee settings del RecastNavMesh (agente/escalones/pendiente/runtime) y dispara reconstruccion.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_settings.json"
res={}
eas=unreal.EditorActorSubsystem()
world=unreal.EditorLevelLibrary.get_editor_world()
rec=None
for a in eas.get_all_level_actors():
    if "RecastNavMesh" in a.get_class().get_name():
        rec=a; break
if rec:
    def gp(n):
        try: return rec.get_editor_property(n)
        except Exception as e: return "n/a"
    res["recast"]={
        "clase":rec.get_class().get_name(),
        "runtime_generation":str(gp("runtime_generation")),
        "cell_size":gp("cell_size"),
        "agent_radius":gp("agent_radius"),
        "agent_height":gp("agent_height"),
        "agent_max_step_height":gp("agent_max_step_height"),
        "agent_max_slope":gp("agent_max_slope"),
        "tile_size_uu":gp("tile_size_uu"),
    }
else:
    res["recast"]="NO ENCONTRADO"
# disparar reconstruccion
try:
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    res["rebuild"]="RebuildNavigation lanzado"
except Exception as e:
    res["rebuild"]="err:"+str(e)[:60]
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
