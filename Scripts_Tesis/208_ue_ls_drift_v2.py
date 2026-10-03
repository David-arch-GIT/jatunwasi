import unreal, json, random
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_drift2.json"
res = {"pasos": [], "err": []}
eas = unreal.EditorActorSubsystem()
CRIAS = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in ("Cria_Karisiri","Cria_Condenado","Cria_Duende"):
        CRIAS[lab] = (a, a.get_actor_location())
        cm = a.get_component_by_class(unreal.CharacterMovementComponent)
        if cm:
            try:
                cm.set_editor_property("gravity_scale", 0.0)
                cm.set_movement_mode(unreal.MovementMode.MOVE_NONE)
            except Exception as e: res["err"].append(lab+"cm:"+str(e)[:25])
at = unreal.AssetToolsHelpers.get_asset_tools()
PKG="/Game/JWN/Cinematics"; NAME="LS_CriaturasDrift"
if unreal.EditorAssetLibrary.does_asset_exist(PKG+"/"+NAME):
    unreal.EditorAssetLibrary.delete_asset(PKG+"/"+NAME)
seq = at.create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
FPS=30; DUR=48
seq.set_display_rate(unreal.FrameRate(FPS,1))
seq.set_playback_start(0); seq.set_playback_end(DUR*FPS)
DR = unreal.MovieSceneTimeUnit.DISPLAY_RATE
AUTO = unreal.MovieSceneKeyInterpolation.AUTO
res["pasos"].append("LS creado")
for lab,(a,loc) in CRIAS.items():
    try:
        b = seq.add_possessable(a)
        tr = b.add_track(unreal.MovieScene3DTransformTrack)
        sec = tr.add_section(); sec.set_range(0, DUR*FPS)
        ch = sec.get_all_channels()
        R=180.0
        wps=[(0,0,0)]
        for i in range(5): wps.append((random.uniform(-R,R),random.uniform(-R,R),random.uniform(-25,25)))
        wps.append((0,0,0))
        n=len(wps)
        for i,(ox,oy,oz) in enumerate(wps):
            f=int(round(i*(DUR*FPS)/(n-1))); fn=unreal.FrameNumber(f)
            ch[0].add_key(fn, loc.x+ox, 0.0, DR, AUTO)
            ch[1].add_key(fn, loc.y+oy, 0.0, DR, AUTO)
            ch[2].add_key(fn, loc.z+oz, 0.0, DR, AUTO)
        res["pasos"].append(lab+" keys ok ("+str(n)+")")
    except Exception as e:
        res["err"].append(lab+":"+str(e)[:70])
unreal.EditorAssetLibrary.save_asset(PKG+"/"+NAME, only_if_is_dirty=False)
# LevelSequenceActor autoplay+loop
try:
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="LSA_CriaturasDrift": eas.destroy_actor(a)
    lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
    lsa.set_actor_label("LSA_CriaturasDrift")
    lsa.set_sequence(seq)
    ps = lsa.get_editor_property("playback_settings")
    ps.set_editor_property("auto_play", True)
    ps.set_editor_property("loop_count", -1)
    lsa.set_editor_property("playback_settings", ps)
    res["pasos"].append("LSA autoplay+loop ok")
except Exception as e:
    res["err"].append("lsa:"+str(e)[:70])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
