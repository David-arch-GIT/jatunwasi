import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/decor_qo.json"
res={"decor_queryonly":0}
eas=unreal.EditorActorSubsystem()
QueryOnly=unreal.CollisionEnabled.QUERY_ONLY
DECOR=["V_Maceta","V_Tinaja","V_Jarron","V_Cantaro","V_Olla","Kit_Vase","Kit_Cirio",
       "S_Amaryllis","Bigleaf_Hydrangea","FN_AlfombraLujo","FN_Cuadro",
       "Decorative_Statuettes","Traditional_Lantern"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl.startswith("HORIZ_ISM") or lbl.startswith("Cartela_"): continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else ""
        if any(k in mn for k in DECOR):
            try:
                c.set_collision_enabled(QueryOnly); res["decor_queryonly"]+=1
            except Exception: pass
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
