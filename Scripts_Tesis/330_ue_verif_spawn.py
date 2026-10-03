# Verifica el arranque: PlayerStart(s) existentes, ubicacion, y que haya NavMesh + GameMode.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_spawn.json"
res={"playerstarts":[], "navmesh":0, "worldsettings_gm":""}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    if cn=="PlayerStart":
        loc=a.get_actor_location()
        res["playerstarts"].append({"label":a.get_actor_label()[:30],"loc":[round(loc.x),round(loc.y),round(loc.z)]})
    if "NavMeshBoundsVolume" in cn:
        res["navmesh"]+=1
res["n_playerstart"]=len(res["playerstarts"])
# GameMode override en WorldSettings
try:
    ws=unreal.EditorLevelLibrary.get_game_mode_override() if hasattr(unreal.EditorLevelLibrary,'get_game_mode_override') else None
except Exception: ws=None
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
    wset=world.get_world_settings()
    gm=wset.get_editor_property("default_game_mode")
    res["worldsettings_gm"]=gm.get_name() if gm else "None (usa DefaultGame.ini=BP_XRGameMode)"
except Exception as e:
    res["worldsettings_gm"]="err:"+str(e)[:40]
open(OUT,"w").write(json.dumps(res,indent=1))
