import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_cubos.json"
res={"cubos_ocultos":[]}
eas=unreal.EditorActorSubsystem()
nombres=["Cube3","Cube4","Cube5","Cube6","Cube7","Cube8","Cube9","Cube10","Cube11","Cube12","Cube24"]
for a in eas.get_all_level_actors():
    if a.get_actor_label() in nombres:
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            ce=str(c.get_collision_enabled()).split(".")[-1]
            hid=c.get_editor_property("hidden_in_game")
            res["cubos_ocultos"].append({"lbl":a.get_actor_label(),"oculto":bool(hid),"colision":ce})
            break
open(OUT,"w").write(json.dumps(res,indent=1))
