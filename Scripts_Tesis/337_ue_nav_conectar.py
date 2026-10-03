# Sube pendiente/escalon max del NavMesh para que la escalera y umbrales conecten las islas. Reconstruye.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_conectar.json"
res={"antes":{}, "despues":{}}
eas=unreal.EditorActorSubsystem()
world=unreal.EditorLevelLibrary.get_editor_world()
rec=None
for a in eas.get_all_level_actors():
    if "RecastNavMesh" in a.get_class().get_name():
        rec=a; break
if rec:
    def g(n):
        try: return rec.get_editor_property(n)
        except Exception: return None
    def s(n,v):
        try: rec.set_editor_property(n,v); return True
        except Exception as e: return str(e)[:40]
    res["antes"]={"slope":g("agent_max_slope"),"step":g("agent_max_step_height")}
    res["set_slope"]=s("agent_max_slope", 54.0)
    res["set_step"]=s("agent_max_step_height", 50.0)
    res["despues"]={"slope":g("agent_max_slope"),"step":g("agent_max_step_height")}
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    res["rebuild"]="lanzado"
else:
    res["err"]="no recast"
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
