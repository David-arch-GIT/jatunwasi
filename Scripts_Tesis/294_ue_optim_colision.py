import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/optim_coll.json"
res={"arboles_queryonly":0, "decor_nocoll":0, "cartela_box_nocoll":0}
eas=unreal.EditorActorSubsystem()
QueryOnly=unreal.CollisionEnabled.QUERY_ONLY
NoColl=unreal.CollisionEnabled.NO_COLLISION
# decoracion menor (sin colision) - solo props claramente no estructurales
DECOR=["V_Maceta","V_Tinaja","V_Jarron","V_Cantaro","V_Olla","Kit_Vase","Kit_Cirio",
       "S_Amaryllis","Bigleaf_Hydrangea","FN_AlfombraLujo","FN_Cuadro",
       "Decorative_Statuettes","Traditional_Lantern"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    # arboles horizonte: QUERY_AND_PHYSICS -> QUERY_ONLY (siguen bloqueando, sin costo de fisica)
    if lbl.startswith("HORIZ_ISM"):
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                if str(c.get_collision_enabled()).split(".")[-1].startswith("QUERY_AND_PHYSICS"):
                    c.set_collision_enabled(QueryOnly)
                    res["arboles_queryonly"]+=1
            except Exception: pass
        continue
    # cajas de colision de cartelas -> sin colision (limpieza pendiente)
    if lbl.startswith("Cartela_"):
        for c in a.get_components_by_class(unreal.BoxComponent):
            c.set_collision_enabled(NoColl); res["cartela_box_nocoll"]+=1
        continue
    # decoracion menor -> sin colision
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else ""
        if any(k in mn for k in DECOR):
            try:
                if not str(c.get_collision_enabled()).split(".")[-1].startswith("NO_COLLISION"):
                    c.set_collision_enabled(NoColl); res["decor_nocoll"]+=1
            except Exception: pass
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
