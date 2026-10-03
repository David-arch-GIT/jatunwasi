import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/duplicados.json"
res={"overlaps":[], "z_bajo":[], "z_raro":[]}
eas=unreal.EditorActorSubsystem()
byloc={}
for a in eas.get_all_level_actors():
    # solo static mesh actors normales
    smcs=a.get_components_by_class(unreal.StaticMeshComponent)
    sm=None
    for c in smcs:
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh")
        if m: sm=m.get_name(); break
    if not sm: continue
    loc=a.get_actor_location()
    key=(sm, round(loc.x/25.0), round(loc.y/25.0), round(loc.z/25.0))
    byloc.setdefault(key, []).append(a.get_actor_label())
# grupos con >1 actor mismo mesh y misma celda ~25u = encimados
for key,labels in byloc.items():
    if len(labels)>1:
        res["overlaps"].append({"mesh":key[0][:28],"cell":[key[1]*25,key[2]*25,key[3]*25],"actores":labels[:6],"n":len(labels)})
res["overlaps"]=sorted(res["overlaps"], key=lambda x:-x["n"])[:30]
res["n_overlaps"]=len(res["overlaps"])
open(OUT,"w").write(json.dumps(res,indent=1))
