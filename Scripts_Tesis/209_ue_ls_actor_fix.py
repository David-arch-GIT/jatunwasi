import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_actor.json"
res = {"pasos": [], "err": []}
eas = unreal.EditorActorSubsystem()
seq = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Cinematics/LS_CriaturasDrift")
# encontrar o crear el LSA
lsa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "LSA_CriaturasDrift":
        lsa = a
if lsa is None:
    lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
    lsa.set_actor_label("LSA_CriaturasDrift")
    res["pasos"].append("LSA creado")
else:
    res["pasos"].append("LSA ya existia")
try:
    lsa.set_sequence(seq)
    ps = lsa.get_editor_property("playback_settings")
    ps.set_editor_property("auto_play", True)
    lc = ps.get_editor_property("loop_count")
    lc.set_editor_property("value", -1)  # infinito
    ps.set_editor_property("loop_count", lc)
    lsa.set_editor_property("playback_settings", ps)
    res["pasos"].append("autoplay=True, loop=infinito")
    # verificar
    ps2 = lsa.get_editor_property("playback_settings")
    res["verif"] = {"auto_play": bool(ps2.get_editor_property("auto_play")), "loop": ps2.get_editor_property("loop_count").get_editor_property("value")}
except Exception as e:
    res["err"].append("cfg:"+str(e)[:70])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
