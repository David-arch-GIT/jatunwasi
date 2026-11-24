# 462_ue_test_voces_mezcla_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai APAGADO via 400) del sistema de voces:
#   PHASE="voces": componentes de audio con sonido de clase SCL_Voz que estan sonando (actor, sonido),
#     tiempo de juego, y si el relato de la plaza ya se reprodujo (DoOnce/colision del trigger).
#   PHASE="push"/"pop": aplica/quita SMX_Conversacion (lo mismo que hace Adela al hablar).
#   PHASE="tp" + TP=(x,y): lleva al pawn (NavMesh, con barrido) a ese punto para disparar una narracion.
#   En todas: "leyendas_disponibles" = trigger de Narr_* aun con colision (no gastado).
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "voces"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test462_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    res["t"] = round(unreal.GameplayStatics.get_time_seconds(world), 1)
    mix = unreal.load_asset("/Game/JWN/Audio/SMX_Conversacion")
    if PHASE == "push":
        unreal.GameplayStatics.push_sound_mix_modifier(world, mix)
    elif PHASE == "pop":
        unreal.GameplayStatics.pop_sound_mix_modifier(world, mix)
    elif PHASE == "tp":
        pw = unreal.GameplayStatics.get_player_pawn(world, 0)
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(TP[0], TP[1], 100), None, None, unreal.Vector(200, 200, 600))
        q = r[0] if isinstance(r, tuple) else r
        pw.set_actor_location(unreal.Vector(q.x, q.y, q.z + 90), True, True)
    disp = {}
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        if a.get_actor_label().startswith(("Narr_", "RELATO_")):
            for tc in a.get_components_by_class(unreal.SphereComponent):
                disp[a.get_actor_label()] = "NO_COLLISION" not in str(tc.get_collision_enabled())
    res["no_gastadas"] = sorted(k for k, v in disp.items() if v)
    res["gastadas"] = sorted(k for k, v in disp.items() if not v)
    sonando = []; voces_total = 0
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        for c in a.get_components_by_class(unreal.AudioComponent):
            s = c.get_editor_property("sound")
            if not s: continue
            try:
                sc = s.get_editor_property("sound_class_object")
            except Exception:
                sc = None
            if sc and sc.get_name() == "SCL_Voz":
                voces_total += 1
                if c.is_playing():
                    sonando.append([a.get_actor_label(), s.get_name()])
            if a.get_actor_label() == "RELATO_plaza":
                for t in a.get_components_by_class(unreal.PrimitiveComponent):
                    if t.get_name().startswith("Trigger"):
                        res["trigger_plaza_colision"] = str(t.get_collision_enabled())
    res["voces_componentes"] = voces_total
    res["sonando"] = sonando
    p = unreal.GameplayStatics.get_player_pawn(world, 0); L = p.get_actor_location(); res["pawn"] = [round(L.x), round(L.y), round(L.z)]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
