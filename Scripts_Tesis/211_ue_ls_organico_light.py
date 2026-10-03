import unreal, json, random, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_light.json"
res = {"keys": {}, "pasos": [], "err": []}
eas = unreal.EditorActorSubsystem()
FPS = 30; DUR = 60
PERS = {
    "Cria_Duende":    {"R":300, "mv":(3.0,6.0), "pp":0.35, "pz":(2.0,4.0), "bob":35},
    "Cria_Condenado": {"R":250, "mv":(5.0,9.0), "pp":0.25, "pz":(3.0,6.0), "bob":20},
    "Cria_Karisiri":  {"R":280, "mv":(4.0,7.0), "pp":0.40, "pz":(2.5,5.0), "bob":30},
}
CRIAS = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in PERS:
        CRIAS[lab] = (a, a.get_actor_location(), a.get_actor_rotation().yaw)
        cm = a.get_component_by_class(unreal.CharacterMovementComponent)
        if cm:
            try: cm.set_editor_property("gravity_scale",0.0); cm.set_movement_mode(unreal.MovementMode.MOVE_NONE)
            except Exception: pass
at = unreal.AssetToolsHelpers.get_asset_tools()
PKG="/Game/JWN/Cinematics"; NAME="LS_CriaturasDrift"
# quitar LSA viejo primero para no dejar referencia colgando
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label()=="LSA_CriaturasDrift": eas.destroy_actor(a)
if unreal.EditorAssetLibrary.does_asset_exist(PKG+"/"+NAME):
    unreal.EditorAssetLibrary.delete_asset(PKG+"/"+NAME)
seq = at.create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS,1)); seq.set_playback_start(0); seq.set_playback_end(DUR*FPS)
DRt = unreal.MovieSceneTimeUnit.DISPLAY_RATE; AUTO = unreal.MovieSceneKeyInterpolation.AUTO
def gen(byaw,P):
    R=P["R"]; ks=[(0.0,0.0,0.0,0.0,byaw)]; t=0.0; cx=0.0; cy=0.0
    while t < DUR-10:
        if random.random() < P["pp"]:
            pd=random.uniform(*P["pz"])
            keys_pause_yaw = byaw + random.uniform(-55,55)
            ks.append((t+pd*0.5, cx, cy, random.uniform(-8,8), keys_pause_yaw))
            t += pd
            ks.append((t, cx, cy, 0.0, byaw + random.uniform(-25,25)))
        else:
            for _ in range(6):
                nx=random.uniform(-R,R); ny=random.uniform(-R,R)
                if nx*nx+ny*ny<=R*R: break
            md=random.uniform(*P["mv"]); yaw=math.degrees(math.atan2(ny-cy,nx-cx))
            t += md
            ks.append((t, nx, ny, random.uniform(-P["bob"],P["bob"]), yaw))
            cx,cy=nx,ny
    ks.append((float(DUR),0.0,0.0,0.0,byaw))
    return ks
for lab,(a,loc,byaw) in CRIAS.items():
    b = seq.add_possessable(a)
    tr = b.add_track(unreal.MovieScene3DTransformTrack); sec = tr.add_section(); sec.set_range(0, DUR*FPS)
    ch = sec.get_all_channels()
    ks = gen(byaw, PERS[lab])
    for (ts,ox,oy,oz,yaw) in ks:
        fn=unreal.FrameNumber(int(round(ts*FPS)))
        ch[0].add_key(fn, loc.x+ox, 0.0, DRt, AUTO)
        ch[1].add_key(fn, loc.y+oy, 0.0, DRt, AUTO)
        ch[2].add_key(fn, loc.z+oz, 0.0, DRt, AUTO)
        ch[5].add_key(fn, yaw, 0.0, DRt, AUTO)
    res["keys"][lab] = len(ks)
unreal.EditorAssetLibrary.save_asset(PKG+"/"+NAME, only_if_is_dirty=False)
lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
lsa.set_actor_label("LSA_CriaturasDrift"); lsa.set_sequence(seq)
ps = lsa.get_editor_property("playback_settings"); ps.set_editor_property("auto_play", True)
lc = ps.get_editor_property("loop_count"); lc.set_editor_property("value",-1); ps.set_editor_property("loop_count",lc)
lsa.set_editor_property("playback_settings", ps)
res["pasos"].append("LSA ok")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
