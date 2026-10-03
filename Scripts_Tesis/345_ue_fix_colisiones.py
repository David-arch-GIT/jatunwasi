# Arreglos seguros: alfombra entrada + arcos convento -> NO_COLLISION (para que el NavMesh pase).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_col.json"
res={"cambios":[]}
eas=unreal.EditorActorSubsystem()
NOCOL=unreal.CollisionEnabled.NO_COLLISION
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    try:
        if "MUS_Alfombra_dorm" in lbl:
            # StaticMeshActor -> su static_mesh_component
            comp=a.get_editor_property("static_mesh_component") if hasattr(a,"get_editor_property") else None
            done=False
            if comp:
                comp.set_collision_enabled(NOCOL); done=True
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_collision_enabled(NOCOL); done=True
            res["cambios"].append({"alfombra":lbl[:30],"nocol":done})
        elif "CONV_ISM_02" == lbl:
            n=0
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                c.set_collision_enabled(NOCOL); n+=1
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_collision_enabled(NOCOL); n+=1
            res["cambios"].append({"arcos_conv":lbl[:30],"comps_nocol":n})
    except Exception as e:
        res["cambios"].append({"err_en":lbl[:30]+":"+str(e)[:50]})
unreal.EditorLoadingAndSavingUtils.save_current_level()
res["guardado"]=True
open(OUT,"w").write(json.dumps(res,indent=1))
