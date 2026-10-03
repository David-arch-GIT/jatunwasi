# Audita faroles: mesh, slots del mesh (default) vs override en el componente. Para restaurar textura real.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_faroles.json"
res={"faroles":[], "resumen":{}}
eas=unreal.EditorActorSubsystem()
def mname(m):
    return m.get_name() if m else "None"
vistos_mesh={}
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    comps=a.get_components_by_class(unreal.StaticMeshComponent)
    for c in comps:
        sm=c.get_editor_property("static_mesh")
        if not sm: continue
        smn=sm.get_name()
        if ("Lantern" not in smn) and ("Farol" not in smn) and ("Farol" not in lbl) and ("Aplique" not in lbl) and ("Lantern" not in lbl):
            continue
        # slots del mesh (default)
        try:
            statmats=sm.get_editor_property("static_materials")
        except Exception:
            statmats=[]
        defaults=[]
        for i,smat in enumerate(statmats):
            try:
                slotname=str(smat.get_editor_property("material_slot_name"))
                mi=smat.get_editor_property("material_interface")
                defaults.append({"slot":slotname,"mat":mname(mi)})
            except Exception as e:
                defaults.append({"slot":"?","mat":"?"})
        # overrides en el componente
        ov=c.get_editor_property("override_materials")
        overrides=[mname(m) for m in ov]
        entry={"actor":lbl[:40],"mesh":smn,"mesh_path":sm.get_path_name(),"n_slots":len(defaults),"defaults":defaults,"overrides":overrides}
        res["faroles"].append(entry)
        vistos_mesh[smn]=vistos_mesh.get(smn,0)+1
res["resumen"]=vistos_mesh
res["total"]=len(res["faroles"])
# recorta para no saturar: guarda 1 ejemplo por mesh + conteos
ejemplos={}
for f in res["faroles"]:
    if f["mesh"] not in ejemplos:
        ejemplos[f["mesh"]]=f
res["ejemplos_por_mesh"]=list(ejemplos.values())
res["faroles"]=res["faroles"][:6]
open(OUT,"w").write(json.dumps(res,indent=1))
