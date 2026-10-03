import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ocultar.json"
res={"ocultados":[]}
eas=unreal.EditorActorSubsystem()
BASIC=["Cube","Sphere","Cylinder","Cone"]
DEF=["BasicShapeMaterial","WorldGridMaterial","DefaultMaterial"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl.startswith("Cartela_"): continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else ""
        if mn not in BASIC: continue
        if c.get_editor_property("hidden_in_game"): continue
        # material por defecto -> bloqueador que quedo visible -> ocultar (mantiene colision)
        isdef=False
        try:
            for i in range(c.get_num_materials()):
                mat=c.get_material(i)
                if mat is None or mat.get_name() in DEF: isdef=True; break
        except Exception: pass
        if isdef:
            c.set_editor_property("hidden_in_game", True)
            res["ocultados"].append(lbl[:30])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ocultados"])
open(OUT,"w").write(json.dumps(res,indent=1))
