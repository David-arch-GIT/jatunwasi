import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/origen_pile.json"
res={"en_origen":[]}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    loc=a.get_actor_location()
    if abs(loc.x)<60 and abs(loc.y)<60 and abs(loc.z)<60:
        # tiene mesh visible?
        vis=False; mn=""
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m=c.get_editor_property("static_mesh")
            if m and not c.get_editor_property("hidden_in_game"):
                vis=True; mn=m.get_name(); break
        res["en_origen"].append({"lbl":a.get_actor_label()[:32],"cls":a.get_class().get_name()[:24],"loc":[round(loc.x),round(loc.y),round(loc.z)],"mesh_visible":mn[:24] if vis else None})
res["n"]=len(res["en_origen"])
open(OUT,"w").write(json.dumps(res,indent=1))
