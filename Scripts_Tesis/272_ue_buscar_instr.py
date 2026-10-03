import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/instr.json"
res={"encontrados":[]}
eas=unreal.EditorActorSubsystem()
KEYS=["charango","zampona","zampoña","quena","acordeon","acordeón","catre"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    low=lbl.lower()
    meshn=""
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m=c.get_editor_property("static_mesh")
        if m: meshn=m.get_name(); break
    hay = any(k in low for k in KEYS) or any(k in meshn.lower() for k in KEYS)
    if hay:
        loc=a.get_actor_location()
        res["encontrados"].append({"lbl":lbl,"mesh":meshn,"loc":[round(loc.x,1),round(loc.y,1),round(loc.z,1)]})
open(OUT,"w").write(json.dumps(res,indent=1))
