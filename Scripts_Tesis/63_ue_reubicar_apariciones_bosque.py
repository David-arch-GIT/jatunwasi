# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Reubica las apariciones AFUERA de las estructuras (bosque/oscuridad): Karisiri afuera del Convento, Condenado afuera del Templo, Duendes en caminos del bosque. Las orienta hacia el jugador, mueve sus AmbientSounds, y REHACE LS_Apariciones para que emerjan y se RETIREN hacia los arboles (apariciones raras, startling). No toca estructura/luces.
# Por que se necesito: El miedo real es verlas afuera en el bosque, asomarse un instante y desvanecerse entre las plantas.
# Resultado obtenido: (pendiente) apariciones en el bosque + animacion retiro.
# ------------------------------------------------------------
import unreal, json, math

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reubicar.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"movidos": []}

# label App3D -> config
CFG = {
    "App3D_Conv_Karisiri": {"xy": (5600, 3400),  "look": (6100, 2900),  "retreat": (-1.0, 0.2),  "gfb": 15.0, "t0": 2.0},
    "App3D_Conv_Condenado":{"xy": (900, 10500),  "look": (300, 9800),   "retreat": (0.8, -0.5),  "gfb": 20.0, "t0": 8.5},
    "App3D_Hac_Duende":    {"xy": (-4300, 500),  "look": (-4300, -200), "retreat": (-0.3, 1.0),  "gfb": 10.0, "t0": 14.5},
    "App3D_Plz_Duende":    {"xy": (3400, 1750),  "look": (3550, 1350),  "retreat": (-0.4, 1.0),  "gfb": 10.0, "t0": 19.5},
}
DUR = 24.0
FPS = 30

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

def ground(x, y, fb):
    try:
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, fb + 60), unreal.Vector(1500, 1500, 1800), None)
        if r is not None and not (abs(r.x) < 0.01 and abs(r.y) < 0.01 and abs(r.z) < 0.01):
            return float(r.z)
    except Exception:
        pass
    return fb

by = {a.get_actor_label(): a for a in all_actors()}

# 1) Mover apariciones + sonidos, orientar
newbase = {}
for lab, c in CFG.items():
    a = by.get(lab)
    if a is None:
        res["movidos"].append({"actor": lab, "err": "no existe"})
        continue
    o, e = a.get_actor_bounds(False)
    half = e.z
    gz = ground(c["xy"][0], c["xy"][1], c["gfb"])
    nz = gz + half
    yaw = math.degrees(math.atan2(c["look"][1] - c["xy"][1], c["look"][0] - c["xy"][0]))
    a.set_actor_location(unreal.Vector(c["xy"][0], c["xy"][1], nz), False, False)
    a.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0), False)
    # mover el sonido asociado
    snd_lab = "Snd_App_" + lab.replace("App3D_", "")
    if snd_lab in by:
        by[snd_lab].set_actor_location(unreal.Vector(c["xy"][0], c["xy"][1], gz + 90), False, False)
    newbase[lab] = {"base": a.get_actor_location(), "scale": a.get_actor_scale3d(), "retreat": c["retreat"], "t0": c["t0"], "gz": round(gz, 1)}
    res["movidos"].append({"actor": lab, "xy": c["xy"], "gz": round(gz, 1), "z": round(nz, 1), "yaw": round(yaw, 1)})

# 2) Rehacer LS_Apariciones (retiro hacia el bosque, apariciones raras)
tools = unreal.AssetToolsHelpers.get_asset_tools()
# destruir el LSA actor primero para liberar la referencia a la secuencia
for a in list(all_actors()):
    if a.get_actor_label() == "LSA_Apariciones":
        unreal.EditorLevelLibrary.destroy_actor(a)
SPATH = "/Game/JWN/Cinematics/LS_Apariciones"
if unreal.EditorAssetLibrary.does_asset_exist(SPATH):
    unreal.EditorAssetLibrary.delete_asset(SPATH)
seq = tools.create_asset("LS_Apariciones", "/Game/JWN/Cinematics", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
if seq is None:
    seq = tools.create_asset("LS_Apariciones_Bosque", "/Game/JWN/Cinematics", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
    SPATH = "/Game/JWN/Cinematics/LS_Apariciones_Bosque"
res["seq"] = seq is not None
seq.set_display_rate(unreal.FrameRate(FPS, 1))
tick = seq.get_tick_resolution()
tps = float(tick.numerator) / float(tick.denominator)
seq.set_playback_start(0)
seq.set_playback_end(int(DUR * FPS))

def fk(sec_t):
    return unreal.FrameNumber(int(round(sec_t * tps)))

for lab, nb in newbase.items():
    a = by[lab]
    base = nb["base"]; sc = nb["scale"]; rt = nb["retreat"]; t0 = nb["t0"]
    binding = seq.add_possessable(a)
    tr = binding.add_track(unreal.MovieScene3DTransformTrack)
    sec = tr.add_section()
    try:
        sec.set_start_frame_seconds(0.0); sec.set_end_frame_seconds(DUR)
    except Exception:
        sec.set_range(0, int(round(DUR * tps)))
    ch = sec.get_all_channels()
    lx, ly, lz, _, _, _, sx, sy, sz = ch[0], ch[1], ch[2], ch[3], ch[4], ch[5], ch[6], ch[7], ch[8]
    def key(c, t, v):
        c.add_key(fk(t), float(v))
    # ventana de aparicion: t0 .. t0+4.9
    t_in = t0 + 1.2; t_hold = t0 + 3.4; t_out = t0 + 4.9
    for c, v in ((sx, sc.x), (sy, sc.y), (sz, sc.z)):
        key(c, 0.0, 0.001); key(c, t0, 0.001); key(c, t_in, v); key(c, t_hold, v); key(c, t_out, 0.001); key(c, DUR, 0.001)
    dx = rt[0] * 230.0; dy = rt[1] * 230.0
    for c, b, d in ((lx, base.x, dx), (ly, base.y, dy), (lz, base.z, 25.0)):
        key(c, 0.0, b); key(c, t0, b); key(c, t_hold, b + d * 0.4); key(c, t_out, b + d); key(c, DUR, b)

unreal.EditorAssetLibrary.save_asset(SPATH)

# 3) LevelSequenceActor auto-play + loop (crear nuevo)
lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0))
lsa.set_actor_label("LSA_Apariciones")
lsa.set_sequence(seq)
ps = lsa.get_editor_property("playback_settings")
ps.set_editor_property("auto_play", True)
lc = unreal.MovieSceneSequenceLoopCount(); lc.set_editor_property("value", -1)
ps.set_editor_property("loop_count", lc)
lsa.set_editor_property("playback_settings", ps)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
unreal.log("REUBICAR listo")
