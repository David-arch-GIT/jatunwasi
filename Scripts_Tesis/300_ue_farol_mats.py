import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/farol_mats.json"
res={"farol_mats":{}, "farol_buenos":[], "farol_rotos":0, "canasta_mats":{}, "lantern_mesh_default":None}
eas=unreal.EditorActorSubsystem()
DEF=["WorldGridMaterial","BasicShapeMaterial","DefaultMaterial",None]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        mn=m.get_name() if m else ""
        if mn=="SM_JW_WallLantern":
            try:
                mat=c.get_material(0)
                nm=mat.get_name() if mat else "None"
                res["farol_mats"][nm]=res["farol_mats"].get(nm,0)+1
                if nm not in [d for d in DEF if d]:
                    res["farol_buenos"].append({"lbl":lbl,"mat":nm})
                else:
                    res["farol_rotos"]+=1
                # material por defecto del mesh (slot override vacio?)
                if res["lantern_mesh_default"] is None and m:
                    dm=m.get_material(0)
                    res["lantern_mesh_default"]=dm.get_name() if dm else "None"
            except Exception: pass
        if "Canasta" in mn:
            try:
                mat=c.get_material(0); nm=mat.get_name() if mat else "None"
                res["canasta_mats"][nm]=res["canasta_mats"].get(nm,0)+1
            except Exception: pass
res["farol_buenos"]=res["farol_buenos"][:5]
open(OUT,"w").write(json.dumps(res,indent=1))
