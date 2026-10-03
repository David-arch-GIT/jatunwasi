import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/scan_bugs.json"
res={"basicshape_visibles":[], "material_default":[], "catre":None, "muy_lejos":[]}
eas=unreal.EditorActorSubsystem()
BASIC=["Cube","Plane","Sphere","Cylinder","Cone"]
DEFMATS=["WorldGridMaterial","DefaultMaterial","BasicShapeMaterial","DefaultDeferredDecalMaterial"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else ""
        vis=not c.get_editor_property("hidden_in_game")
        # forma basica VISIBLE (no cartela ni cuadro)
        if mn in BASIC and vis and not lbl.startswith("Cartela_"):
            loc=a.get_actor_location()
            res["basicshape_visibles"].append({"lbl":lbl[:30],"mesh":mn,"loc":[round(loc.x),round(loc.y),round(loc.z)]})
        # material por defecto (rosa/gris) en algo visible
        if vis:
            try:
                for i in range(c.get_num_materials()):
                    mat=c.get_material(i)
                    if mat is None or mat.get_name() in DEFMATS:
                        res["material_default"].append({"lbl":lbl[:30],"mesh":mn[:24],"slot":i,"mat":(mat.get_name() if mat else "None")})
            except Exception: pass
    if lbl=="CV2_Catre":
        loc=a.get_actor_location()
        wl=None
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            wl=c.get_world_location(); break
        res["catre"]={"actor_loc":[round(loc.x),round(loc.y),round(loc.z)], "comp_wloc":[round(wl.x),round(wl.y),round(wl.z)] if wl else None, "visible": bool(wl)}
res["basicshape_visibles"]=res["basicshape_visibles"][:40]
res["material_default"]=res["material_default"][:40]
res["n_basic"]=len(res["basicshape_visibles"]); res["n_defmat"]=len(res["material_default"])
open(OUT,"w").write(json.dumps(res,indent=1))
