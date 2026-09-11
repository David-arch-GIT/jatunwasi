# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Rehace LS_Apariciones con animacion CONFIABLE y profesional: cada aparicion EMPIEZA VISIBLE en el borde del bosque mirando al jugador, permanece ~7s (con leve flotar), se RETIRA hacia los arboles y desaparece ~4s, y re-emerge. Loop 14s. Conserva orientacion (yaw) hacia el jugador. LSA auto_play + loop.
# Por que se necesito: El usuario no veia las apariciones (estaban invisibles casi todo el tiempo). Deben verse seguido y desde el inicio.
# Resultado obtenido: (pendiente) apariciones visibles y confiables.
# ------------------------------------------------------------
import unreal, json, math

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/anim65.json"
res = {}
DUR = 14.0
FPS = 30
tools = unreal.AssetToolsHelpers.get_asset_tools()

RETREAT = {
    "App3D_Conv_Karisiri":  (-1.0, 0.2),
    "App3D_Conv_Condenado": (0.8, -0.5),
    "App3D_Hac_Duende":     (-0.3, 1.0),
    "App3D_Plz_Duende":     (-0.4, 1.0),
}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

by = {a.get_actor_label(): a for a in all_actors()}

# destruir LSA para liberar la secuencia
for a in list(all_actors()):
    if a.get_actor_label() == "LSA_Apariciones":
        unreal.EditorLevelLibrary.destroy_actor(a)
SPATH = "/Game/JWN/Cinematics/LS_Apariciones"
if unreal.EditorAssetLibrary.does_asset_exist(SPATH):
    unreal.EditorAssetLibrary.delete_asset(SPATH)
seq = tools.create_asset("LS_Apariciones", "/Game/JWN/Cinematics", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
res["seq"] = seq is not None
seq.set_display_rate(unreal.FrameRate(FPS, 1))
tick = seq.get_tick_resolution()
tps = float(tick.numerator) / float(tick.denominator)
seq.set_playback_start(0)
seq.set_playback_end(int(DUR * FPS))

def fk(t): return unreal.FrameNumber(int(round(t * tps)))

res["apps"] = []
for lab, rt in RETREAT.items():
    a = by.get(lab)
    if a is None:
        continue
    base = a.get_actor_location()
    sc = a.get_actor_scale3d()
    yaw = a.get_actor_rotation().yaw
    mag = math.hypot(rt[0], rt[1]) or 1.0
    dx = rt[0] / mag * 360.0
    dy = rt[1] / mag * 360.0
    deep = unreal.Vector(base.x + dx, base.y + dy, base.z)

    binding = seq.add_possessable(a)
    tr = binding.add_track(unreal.MovieScene3DTransformTrack)
    sec = tr.add_section()
    try:
        sec.set_start_frame_seconds(0.0); sec.set_end_frame_seconds(DUR)
    except Exception:
        sec.set_range(0, int(round(DUR * tps)))
    ch = sec.get_all_channels()
    lx, ly, lz, rr, rp, ryaw, sx, sy, sz = ch

    def key(c, t, v):
        c.add_key(fk(t), float(v))

    # ESCALA: visible 0-7, se va 7-9, oculta 9-11, re-emerge 11-14
    for c, v in ((sx, sc.x), (sy, sc.y), (sz, sc.z)):
        key(c, 0.0, v); key(c, 7.0, v); key(c, 9.0, 0.01); key(c, 11.0, 0.01); key(c, DUR, v)
    # POSICION: borde 0-7, retira a bosque 7-9, deep 9-11, vuelve a borde 11-14 (+ leve flotar)
    for c, b, d in ((lx, base.x, deep.x - base.x), (ly, base.y, deep.y - base.y)):
        key(c, 0.0, b); key(c, 7.0, b); key(c, 9.0, b + d); key(c, 11.0, b + d); key(c, DUR, b)
    # Z con leve flotar mientras visible
    key(lz, 0.0, base.z); key(lz, 3.5, base.z + 10.0); key(lz, 7.0, base.z)
    key(lz, 9.0, deep.z); key(lz, 11.0, deep.z); key(lz, DUR, base.z)
    # YAW constante mirando al jugador
    key(ryaw, 0.0, yaw); key(ryaw, DUR, yaw)

    res["apps"].append(lab)

unreal.EditorAssetLibrary.save_asset(SPATH)

# LSA nuevo con auto_play + loop
lsa = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0, 0, 0))
lsa.set_actor_label("LSA_Apariciones")
lsa.set_sequence(seq)
ps = lsa.get_editor_property("playback_settings")
ps.set_editor_property("auto_play", True)
lc = unreal.MovieSceneSequenceLoopCount(); lc.set_editor_property("value", -1)
ps.set_editor_property("loop_count", lc)
lsa.set_editor_property("playback_settings", ps)
res["auto_play"] = bool(ps.get_editor_property("auto_play"))
res["loop"] = ps.get_editor_property("loop_count").get_editor_property("value")

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("ANIM65 confiable listo")
