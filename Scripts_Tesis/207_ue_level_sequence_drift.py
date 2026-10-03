import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ls_drift.json"
res = {"pasos": [], "err": []}
eas = unreal.EditorActorSubsystem()
# 1) preparar criaturas: gravedad 0, movimiento desactivado (para que el LS controle)
CRIAS = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab not in ("Cria_Karisiri", "Cria_Condenado", "Cria_Duende"): continue
    loc = a.get_actor_location(); rot = a.get_actor_rotation()
    CRIAS[lab] = (a, loc, rot)
    cm = a.get_component_by_class(unreal.CharacterMovementComponent)
    if cm:
        try:
            cm.set_editor_property("gravity_scale", 0.0)
            cm.set_movement_mode(unreal.MovementMode.MOVE_NONE)
        except Exception as e: res["err"].append(lab+" cm:"+str(e)[:30])
res["pasos"].append("criaturas preparadas: %d" % len(CRIAS))
# 2) crear Level Sequence
at = unreal.AssetToolsHelpers.get_asset_tools()
PKG = "/Game/JWN/Cinematics"; NAME = "LS_CriaturasDrift"
if unreal.EditorAssetLibrary.does_asset_exist(PKG+"/"+NAME):
    unreal.EditorAssetLibrary.delete_asset(PKG+"/"+NAME)
seq = at.create_asset(NAME, PKG, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(30, 1))
FPS = 30; DUR_S = 48
seq.set_playback_start(0)
seq.set_playback_end(DUR_S * FPS)
res["pasos"].append("LS creado")
# 3) por cada criatura: bind + transform track + keys de drift
import random
def add_drift(lab, actor, loc, rot):
    try:
        binding = seq.add_possessable(actor)
        track = binding.add_track(unreal.MovieScene3DTransformTrack)
        section = track.add_section()
        section.set_range(0, DUR_S * FPS)
        chans = section.get_all_channels()  # [locX,locY,locZ, rotX,rotY,rotZ, scaleX,scaleY,scaleZ]
        # waypoints de drift dentro de +-180 en XY, +-25 en Z (bob), volviendo al inicio
        R = 180.0
        wps = [(0.0,0.0,0.0)]
        for i in range(5):
            wps.append((random.uniform(-R,R), random.uniform(-R,R), random.uniform(-25,25)))
        wps.append((0.0,0.0,0.0))  # cierra el bucle
        n = len(wps)
        for i,(ox,oy,oz) in enumerate(wps):
            f = int(round(i*(DUR_S*FPS)/(n-1)))
            fn = unreal.FrameNumber(f)
            chans[0].add_key(fn, loc.x+ox, 0.0, unreal.SequenceTimeUnit.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
            chans[1].add_key(fn, loc.y+oy, 0.0, unreal.SequenceTimeUnit.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
            chans[2].add_key(fn, loc.z+oz, 0.0, unreal.SequenceTimeUnit.DISPLAY_RATE, unreal.MovieSceneKeyInterpolation.AUTO)
        res["pasos"].append(lab+" drift keys ok")
    except Exception as e:
        res["err"].append(lab+" drift:"+str(e)[:60])
for lab,(a,loc,rot) in CRIAS.items():
    add_drift(lab, a, loc, rot)
unreal.EditorAssetLibrary.save_asset(PKG+"/"+NAME, only_if_is_dirty=False)
# 4) LevelSequenceActor con autoplay + loop
try:
    lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0,0,0))
    lsa.set_actor_label("LSA_CriaturasDrift")
    lsa.set_sequence(seq)
    lsa.set_editor_property("auto_play", True)
    ps = lsa.get_editor_property("playback_settings")
    ps.set_editor_property("loop_count", -1)  # infinito
    lsa.set_editor_property("playback_settings", ps)
    res["pasos"].append("LSA autoplay+loop ok")
except Exception as e:
    res["err"].append("lsa:"+str(e)[:60])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
