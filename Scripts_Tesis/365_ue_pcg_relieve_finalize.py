import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_final.json"
res={"test_removed":0,"relieve_inst":0}
eas=unreal.EditorActorSubsystem()
# restaurar luz nocturna
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    if cn=="DirectionalLight":
        c=a.get_component_by_class(unreal.DirectionalLightComponent); c.set_editor_property("intensity",0.7)
    if cn=="SkyLight":
        c=a.get_component_by_class(unreal.SkyLightComponent)
        try: c.set_editor_property("intensity",1.2)
        except: pass
# borrar test SMAs
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label().startswith("REL_TEST_"):
        eas.destroy_actor(a); res["test_removed"]+=1
# contar relieve
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="PCG_RelieveVol":
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            res["relieve_inst"]+=c.get_instance_count()
        break
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
