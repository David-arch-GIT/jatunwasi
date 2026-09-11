# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Crea un Level Sequence (LS_Apariciones) que anima los App3D_* : se materializan (escala 0->1), derivan hacia afuera y flotan levemente, y se desvanecen (escala 1->0), en bucle escalonado. Coloca un LevelSequenceActor con auto-play + loop infinito.
# Por que se necesito: Dar movimiento/animacion a las apariciones (aparecer, permanecer, desvanecerse) sin depender de triggers.
# Resultado obtenido: (pendiente) apariciones animadas en bucle.
# ------------------------------------------------------------
import unreal, json, math

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/anim_seq.json"
res = {"pasos": []}
tools = unreal.AssetToolsHelpers.get_asset_tools()
FOLDER = "/Game/JWN/Cinematics"
SPATH = FOLDER + "/LS_Apariciones"

if unreal.EditorAssetLibrary.does_asset_exist(SPATH):
    unreal.EditorAssetLibrary.delete_asset(SPATH)
seq = tools.create_asset("LS_Apariciones", FOLDER, unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
FPS = 30
DUR = 15.0   # bucle de 15 s
seq.set_display_rate(unreal.FrameRate(FPS, 1))
tick = seq.get_tick_resolution()
tps = float(tick.numerator) / float(tick.denominator)   # ticks por segundo
seq.set_playback_start(0)
seq.set_playback_end(int(DUR * FPS))

def fn(sec):
    return unreal.FrameNumber(int(round(sec * tps)))

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

apps = [a for a in all_actors() if a.get_actor_label().startswith("App3D_")]
res["apps"] = [a.get_actor_label() for a in apps]

# escala base actual de cada actor
for i, a in enumerate(apps):
    base_scale = a.get_actor_scale3d()
    loc0 = a.get_actor_location()
    # direccion de deriva: alejandose del centro de su zona (hacia sombras/arboles)
    # usar el propio vector desde un centro aproximado
    off = i * 3.0  # escalonado 3s entre apariciones
    # tiempos dentro del bucle (con wrap simple: mantenemos dentro de DUR)
    t_app0 = off % DUR
    t_full = (off + 1.6) % DUR
    t_hold = (off + 7.0) % DUR
    t_gone = (off + 8.6) % DUR

    binding = seq.add_possessable(a)
    tr = binding.add_track(unreal.MovieScene3DTransformTrack)
    sec = tr.add_section()
    try:
        sec.set_start_frame_seconds(0.0)
        sec.set_end_frame_seconds(DUR)
    except Exception:
        sec.set_range(0, int(round(DUR * tps)))
    chans = sec.get_all_channels()
    # orden: 0..2 loc, 3..5 rot, 6..8 scale
    locx, locy, locz = chans[0], chans[1], chans[2]
    sx, sy, sz = chans[6], chans[7], chans[8]

    # deriva: sube 40cm y se aleja un poco en Y
    drift = unreal.Vector(0.0, -180.0, 45.0)

    def key(ch, sec_t, val):
        ch.add_key(unreal.FrameNumber(int(round(sec_t * tps))), float(val))

    # ESCALA (materializar / desvanecer) — clave: 0 fuera, base dentro
    for ch, comp in ((sx, base_scale.x), (sy, base_scale.y), (sz, base_scale.z)):
        key(ch, 0.0, 0.001)
        key(ch, t_app0, 0.001)
        key(ch, t_full, comp)
        key(ch, t_hold, comp)
        key(ch, t_gone, 0.001)
        key(ch, DUR, 0.001)

    # POSICION (deriva mientras esta visible)
    for ch, base_c, d in ((locx, loc0.x, drift.x), (locy, loc0.y, drift.y), (locz, loc0.z, drift.z)):
        key(ch, 0.0, base_c)
        key(ch, t_full, base_c)
        key(ch, t_hold, base_c + d)
        key(ch, DUR, base_c)

res["pasos"].append("tracks creados para %d apariciones" % len(apps))
unreal.EditorAssetLibrary.save_asset(SPATH)

# LevelSequenceActor con auto-play + loop
lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0))
lsa.set_actor_label("LSA_Apariciones")
lsa.set_sequence(seq)
try:
    lsa.set_editor_property("auto_play", True)
    ps = lsa.get_editor_property("playback_settings")
    try:
        ps.set_editor_property("loop_count", -1)
    except Exception:
        try:
            lc = ps.get_editor_property("loop_count")
            lc.set_editor_property("value", -1)
            ps.set_editor_property("loop_count", lc)
        except Exception as e2:
            res["loop_err"] = str(e2)
    lsa.set_editor_property("playback_settings", ps)
    res["autoplay"] = "ok"
except Exception as e:
    res["autoplay_err"] = str(e)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("ANIM SEQ listo")
