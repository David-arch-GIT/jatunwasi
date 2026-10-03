# QA final Quest: Nanite (no soportado bien), materiales de skeletals (apariciones), meshes muy pesados visibles.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/qa_final.json"
res={"nanite_on":[], "skel_bugs":[], "skel_ok":[], "pesados":[], "mesh_nulos_visibles":[]}
BAD={"WorldGridMaterial","DefaultMaterial","BasicShapeMaterial"}
eas=unreal.EditorActorSubsystem()
meshes_vistos=set()
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()[:38]
    # --- static meshes: Nanite + pesados ---
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            hig=c.get_editor_property("hidden_in_game"); vis=c.get_editor_property("visible")
        except Exception: hig=False; vis=True
        sm=c.get_editor_property("static_mesh")
        if not sm: continue
        smn=sm.get_name()
        if smn in meshes_vistos:
            pass
        else:
            meshes_vistos.add(smn)
            # nanite
            try:
                ns=sm.get_editor_property("nanite_settings")
                if ns and ns.get_editor_property("enabled"):
                    res["nanite_on"].append(smn)
            except Exception: pass
            # triangulos LOD0
            try:
                tri=unreal.EditorStaticMeshLibrary.get_number_of_triangles(sm,0)
                if tri>60000 and not hig and vis:
                    res["pesados"].append({"mesh":smn,"tris":tri,"actor":lbl})
            except Exception: pass
    # --- skeletal: materiales grid + info ---
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            hig=c.get_editor_property("hidden_in_game"); vis=c.get_editor_property("visible")
        except Exception: hig=False; vis=True
        sk=c.get_editor_property("skeletal_mesh")
        if not sk: continue
        ov=c.get_editor_property("override_materials")
        try: mats=sk.get_editor_property("materials")
        except Exception: mats=[]
        n=max(len(ov),len(mats))
        badfound=False
        names=[]
        for i in range(n):
            m=None
            if i<len(ov) and ov[i]: m=ov[i]
            elif i<len(mats):
                try: m=mats[i].get_editor_property("material_interface")
                except Exception: m=None
            nm=m.get_name() if m else "None"
            names.append(nm)
            if (m is None) or (nm in BAD): badfound=True
        entry={"actor":lbl,"skmesh":sk.get_name(),"mats":names,"visible":(vis and not hig)}
        if badfound and vis and not hig: res["skel_bugs"].append(entry)
        else: res["skel_ok"].append(entry)
res["n_nanite"]=len(res["nanite_on"]); res["n_skel_bugs"]=len(res["skel_bugs"]); res["n_pesados"]=len(res["pesados"])
res["nanite_on"]=res["nanite_on"][:30]; res["pesados"]=res["pesados"][:20]
open(OUT,"w").write(json.dumps(res,indent=1))
