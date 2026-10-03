import unreal, json, random, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_organico.json"
res = {"pasos": [], "keys_por_cria": {}, "err": []}
eas = unreal.EditorActorSubsystem()
FPS = 30; DUR = 90  # 90s de recorrido variado (se siente no-repetitivo)
# personalidad por criatura: R(radio drift), rango dur_mov(s), prob_pausa, rango pausa(s)
PERS = {
    "Cria_Duende":    {"R":300, "mv":(1.5,4.0), "pp":0.35, "pz":(1.5,4.0), "bob":35},  # inquieto, rapido
    "Cria_Condenado": {"R":250, "mv":(4.0,8.0), "pp":0.25, "pz":(3.0,6.0), "bob":20},  # lento, pesado
    "Cria_Karisiri":  {"R":280, "mv":(2.5,5.0), "pp":0.45, "pz":(2.0,5.0), "bob":30},  # acechador
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
# recrear LS
at = unreal.AssetToolsHelpers.get_asset_tools()
PKG="/Game/JWN/Cinematics"; NAME="LS_CriaturasDrift"
if unreal.EditorAssetLibrary.does_asset_exist(PKG+"/"+NAME):
    unreal.EditorAssetLibrary.delete_asset(PKG+"/"+NAME)
seq = at.create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(FPS,1)); seq.set_playback_start(0); seq.set_playback_end(DUR*FPS)
DRt = unreal.MovieSceneTimeUnit.DISPLAY_RATE; AUTO = unreal.MovieSceneKeyInterpolation.AUTO
def gen_keys(base_yaw, P):
    R=P["R"]; keys=[(0.0, 0.0,0.0,0.0, base_yaw)]
    t=0.0; cx=0.0; cy=0.0
    random.seed()
    while t < DUR-8:
        if random.random() < P["pp"]:
            # PAUSA: se detiene y mira alrededor (varios yaw, misma pos)
            pd = random.uniform(*P["pz"]); nlk = random.randint(1,2)
            for j in range(1,nlk+1):
                t2 = t + pd*j/(nlk+1)
                ylook = base_yaw + random.uniform(-60,60)
                keys.append((t2, cx, cy, random.uniform(-8,8), ylook))
            t += pd
            keys.append((t, cx, cy, 0.0, base_yaw + random.uniform(-25,25)))
        else:
            # MOVE a punto aleatorio dentro del radio (velocidad variable = dur variable)
            for _ in range(8):
                nx=random.uniform(-R,R); ny=random.uniform(-R,R)
                if nx*nx+ny*ny <= R*R: break
            md = random.uniform(*P["mv"])
            yaw = math.degrees(math.atan2(ny-cy, nx-cx))  # gira hacia donde va
            t += md
            keys.append((t, nx, ny, random.uniform(-P["bob"],P["bob"]), yaw))
            cx,cy = nx,ny
    keys.append((float(DUR), 0.0,0.0,0.0, base_yaw))  # cierra el bucle en el centro
    return keys
for lab,(a,loc,byaw) in CRIAS.items():
    try:
        b = seq.add_possessable(a)
        tr = b.add_track(unreal.MovieScene3DTransformTrack); sec = tr.add_section(); sec.set_range(0, DUR*FPS)
        ch = sec.get_all_channels()
        ks = gen_keys(byaw, PERS[lab])
        for (ts, ox,oy,oz, yaw) in ks:
            fn = unreal.FrameNumber(int(round(ts*FPS)))
            ch[0].add_key(fn, loc.x+ox, 0.0, DRt, AUTO)
            ch[1].add_key(fn, loc.y+oy, 0.0, DRt, AUTO)
            ch[2].add_key(fn, loc.z+oz, 0.0, DRt, AUTO)
            ch[5].add_key(fn, yaw, 0.0, DRt, AUTO)  # yaw (girar/mirar)
        res["keys_por_cria"][lab] = len(ks)
    except Exception as e:
        res["err"].append(lab+":"+str(e)[:70])
unreal.EditorAssetLibrary.save_asset(PKG+"/"+NAME, only_if_is_dirty=False)
# LSA autoplay+loop
try:
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="LSA_CriaturasDrift": eas.destroy_actor(a)
    lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
    lsa.set_actor_label("LSA_CriaturasDrift"); lsa.set_sequence(seq)
    ps = lsa.get_editor_property("playback_settings"); ps.set_editor_property("auto_play", True)
    lc = ps.get_editor_property("loop_count"); lc.set_editor_property("value",-1); ps.set_editor_property("loop_count",lc)
    lsa.set_editor_property("playback_settings", ps)
    res["pasos"].append("LSA autoplay+loop ok")
except Exception as e: res["err"].append("lsa:"+str(e)[:60])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
