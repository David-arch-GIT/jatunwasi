# 488_ue_test_concurrencia_real.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (PIE, Convai apagado) verificar la concurrencia REAL de voces: reproduce dos voces del grupo
#   SC_Narracion y vuelca con au.DumpActiveSounds lo que el motor tiene sonando (va al log).
#   PHASE="a": Play de RELATO_convento (prio 1). PHASE="b": Play de la frase de Adela (prio 0.5) en un
#   componente 2D temporal. PHASE="c": Play de RELATO_hacienda (prio 1, mas nuevo). PHASE="dump": vuelca.
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "dump"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test488_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    acts = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)}
    def narr(lb):
        return [c for c in acts[lb].get_components_by_class(unreal.AudioComponent) if c.get_name().startswith("Narration")][0]
    if PHASE == "a":
        narr("RELATO_convento").play()
    elif PHASE == "b":
        unreal.GameplayStatics.play_sound2d(world, unreal.load_asset("/Game/JWN/Audio/Guia/A_Guia_Preguntas"))
    elif PHASE == "c":
        narr("RELATO_hacienda").play()
    elif PHASE == "dump":
        unreal.SystemLibrary.execute_console_command(world, "au.DumpActiveSounds")
    res["playing"] = {lb: narr(lb).is_playing() for lb in ("RELATO_convento", "RELATO_hacienda")}
except Exception:
    res["err"] = traceback.format_exc()[:1000]
open(OUT, "w").write(json.dumps(res))
