import unreal, json, random, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_natural.json"
res = {"keys": {}, "walk": {}, "err": []}
eas = unreal.EditorActorSubsystem()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
FPS=30; DUR=45; DT=1.8
# personalidad: R radio, spd velocidad(u/s), turn giro max por paso(grados)
PERS = {
    "Cria_Duende":    {"R":320, "spd":105, "turn":28, "yawoff":90},
    "Cria_Condenado": {"R":240, "spd":72,  "turn":14, "yawoff":90},
    "Cria_Karisiri":  {"R":270, "spd":90,  "turn":22, "yawoff":90},
}
def find_walk(cre):
    for a in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","AnimSequence"), True):
        p=str(a.package_name); low=p.lower()
        if cre in low and "walk" in low: return unreal.EditorAssetLibrary.load_asset(p)
    return None
CRIAS={}
for a in eas.get_all_level_actors():
    lab=a.get_actor_label()
    if lab in PERS:
        CRIAS[lab]=(a, a.get_actor_location())
        cm=a.get_component_by_class(unreal.CharacterMovementComponent)
        if cm:
            try: cm.set_editor_property("gravity_scale",0.0); cm.set_movement_mode(unreal.MovementMode.MOVE_NONE)
            except Exception: pass
        # WALK single-node loop (mueve los pies)
        cre = "duende" if "duende" in lab.lower() else ("condenado" if "condenado" in lab.lower() else "karisiri")
        wk = find_walk(cre)
        res["walk"][lab] = wk.get_name() if wk else "NO"
        mc=a.get_component_by_class(unreal.SkeletalMeshComponent)
        if mc and wk:
            try:
                mc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
                spd=unreal.SingleAnimationPlayData(); spd.set_editor_property("anim_to_play", wk)
                spd.set_editor_property("saved_looping", True); spd.set_editor_property("saved_playing", True)
                mc.set_editor_property("animation_data", spd)
            except Exception as e: res["err"].append(lab+"walk:"+str(e)[:30])
# recrear LS
at=unreal.AssetToolsHelpers.get_asset_tools(); PKG="/Game/JWN/Cinematics"; NAME="LS_CriaturasDrift"
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label()=="LSA_CriaturasDrift": eas.destroy_actor(a)
if unreal.EditorAssetLibrary.does_asset_exist(PKG+"/"+NAME): unreal.EditorAssetLibrary.delete_asset(PKG+"/"+NAME)
seq=at.create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS,1)); seq.set_playback_start(0); seq.set_playback_end(DUR*FPS)
DRt=unreal.MovieSceneTimeUnit.DISPLAY_RATE; AUTO=unreal.MovieSceneKeyInterpolation.AUTO
def wander(P):
    R=P["R"]; spd=P["spd"]; turn=P["turn"]; yo=P["yawoff"]
    heading=random.uniform(0,360); px=0.0; py=0.0; t=0.0
    ks=[(0.0,0.0,0.0, heading+yo)]
    while t < DUR:
        heading += random.uniform(-turn,turn)
        dc=math.sqrt(px*px+py*py)
        if dc > R*0.62:
            ac=math.degrees(math.atan2(-py,-px))
            # girar suave hacia el centro
            diff=((ac-heading+180)%360)-180
            heading += diff*0.45
        s=spd*random.uniform(0.65,1.05)*DT
        px += math.cos(math.radians(heading))*s
        py += math.sin(math.radians(heading))*s
        d=math.sqrt(px*px+py*py)
        if d>R: px*=R/d; py*=R/d
        t+=DT
        ks.append((t, px, py, heading+yo))
    return ks
for lab,(a,loc) in CRIAS.items():
    b=seq.add_possessable(a); tr=b.add_track(unreal.MovieScene3DTransformTrack); sec=tr.add_section(); sec.set_range(0,DUR*FPS)
    ch=sec.get_all_channels(); ks=wander(PERS[lab])
    for (ts,ox,oy,yaw) in ks:
        fn=unreal.FrameNumber(int(round(ts*FPS)))
        ch[0].add_key(fn, loc.x+ox, 0.0, DRt, AUTO)
        ch[1].add_key(fn, loc.y+oy, 0.0, DRt, AUTO)
        ch[2].add_key(fn, loc.z, 0.0, DRt, AUTO)
        ch[5].add_key(fn, yaw, 0.0, DRt, AUTO)
    res["keys"][lab]=len(ks)
unreal.EditorAssetLibrary.save_asset(PKG+"/"+NAME, only_if_is_dirty=False)
lsa=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
lsa.set_actor_label("LSA_CriaturasDrift"); lsa.set_sequence(seq)
ps=lsa.get_editor_property("playback_settings"); ps.set_editor_property("auto_play",True)
lc=ps.get_editor_property("loop_count"); lc.set_editor_property("value",-1); ps.set_editor_property("loop_count",lc)
lsa.set_editor_property("playback_settings",ps)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
