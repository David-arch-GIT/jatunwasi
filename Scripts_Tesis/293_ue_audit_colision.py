import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_coll.json"
res={"instanced_con_colision":[], "instanced_sin_colision_count":0, "sm_colision_por_mesh":{}, "total_instancias_con_colision":0}
eas=unreal.EditorActorSubsystem()
def ce_name(c):
    try: return str(c.get_collision_enabled()).split(".")[-1]
    except Exception: return "?"
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    # instanced (HISM/ISM) - los mas pesados por conteo
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try: n=c.get_instance_count()
        except Exception: n=0
        ce=ce_name(c)
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else "?"
        if ce not in ("NO_COLLISION","NoCollision"):
            res["instanced_con_colision"].append({"actor":lbl[:28],"mesh":mn[:30],"inst":n,"coll":ce})
            res["total_instancias_con_colision"]+=n
        else:
            res["instanced_sin_colision_count"]+=1
    # static mesh comps (no instanced) con colision -> agrupar por mesh
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        ce=ce_name(c)
        if ce in ("NO_COLLISION","NoCollision"): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else "?"
        key=mn[:34]
        res["sm_colision_por_mesh"][key]=res["sm_colision_por_mesh"].get(key,0)+1
# ordenar
res["instanced_con_colision"]=sorted(res["instanced_con_colision"], key=lambda x:-x["inst"])[:25]
res["sm_colision_por_mesh"]=dict(sorted(res["sm_colision_por_mesh"].items(), key=lambda x:-x[1])[:30])
open(OUT,"w").write(json.dumps(res,indent=1))
