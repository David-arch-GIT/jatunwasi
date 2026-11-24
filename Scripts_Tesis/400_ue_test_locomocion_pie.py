# 400_ue_test_locomocion_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba del movimiento fluido nuevo de BP_XRPawn SIN gastar Convai.
#   PHASE="convai_off": apaga auto_initialize_session (Pawn ConvaiPlayer + Adela chatbot) SIN guardar.
#   PHASE="test": (durante PIE) replica paso a paso la logica del grafo (rayo 45 cm a 60 cm +
#     proyeccion NavMesh 40 cm) moviendo al pawn real: hacia barrera cerrada, por sendero,
#     hacia el campo, y luego con la barrera abierta.
#   PHASE="convai_on": restaura auto_initialize_session=True y verifica.
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "test"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test400_%s.json" % PHASE
res = {"phase": PHASE, "err": None}

def convai_flags(value):
    out = []
    bp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
        if o and o.get_class().get_name() == "ConvaiPlayerComponent":
            o.set_editor_property("auto_initialize_session", value)
            out.append(["pawn", o.get_editor_property("auto_initialize_session")])
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        for c in a.get_components_by_class(unreal.ActorComponent):
            if c.get_class().get_name() == "ConvaiChatbotComponent":
                c.set_editor_property("auto_initialize_session", value)
                out.append([a.get_actor_label(), c.get_editor_property("auto_initialize_session")])
    return out

try:
    if PHASE == "convai_off":
        res["flags"] = convai_flags(False)
    elif PHASE == "convai_on":
        res["flags"] = convai_flags(True)
        bp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    else:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        res["world"] = world.get_name() if world else None
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        res["pawn"] = pawn.get_class().get_name() if pawn else None
        L = pawn.get_actor_location(); res["spawn_loc"] = [round(L.x), round(L.y), round(L.z)]

        def step_walk(dirx, diry, steps, step_len=3.5):
            n = math.hypot(dirx, diry); dx, dy = dirx / n, diry / n
            moved = 0; stop = None
            for i in range(steps):
                cur = pawn.get_actor_location()
                start = unreal.Vector(cur.x, cur.y, cur.z + 60)
                end = unreal.Vector(start.x + dx * 45, start.y + dy * 45, start.z)
                hit = unreal.SystemLibrary.line_trace_single(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                             False, [pawn], unreal.DrawDebugTrace.NONE, True)
                h = hit if isinstance(hit, unreal.HitResult) else next((e for e in (hit if isinstance(hit, tuple) else []) if isinstance(e, unreal.HitResult)), None)
                if h is not None and h.to_tuple()[0]:
                    t = h.to_tuple(); stop = "WALL:" + str(t[9].get_name() if len(t) > 9 and t[9] else "?")
                    break
                des = unreal.Vector(cur.x + dx * step_len, cur.y + dy * step_len, cur.z)
                r = unreal.NavigationSystemV1.project_point_to_navigation(world, des, None, None, unreal.Vector(40, 40, 300))
                loc = r[0] if isinstance(r, tuple) else r
                if loc is None:
                    stop = "NAV_EDGE"; break
                pawn.set_actor_location(loc, False, False)
                moved += step_len
            c = pawn.get_actor_location()
            return {"moved_cm": round(moved), "stop": stop, "end": [round(c.x), round(c.y), round(c.z)]}

        def tp(x, y):
            r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 100), None, None, unreal.Vector(100, 100, 400))
            loc = r[0] if isinstance(r, tuple) else r
            pawn.set_actor_location(loc, False, False)

        tests = {}
        # 1) Hacia la barrera de Hacienda (cerrada al inicio): desde (-900,-1000) caminar hacia -X
        tp(-900, -1000); tests["hacia_barrera_hacienda_cerrada"] = step_walk(-1, 0, 400)
        # 2) Sendero al templo: desde (247,2124) hacia el norte
        tp(247, 2124); tests["sendero_templo_norte_14m"] = step_walk(0, 1, 400)
        # 3) Hacia el campo (fuera del sendero): desde (247,2124) hacia +X
        tp(247, 2124); tests["hacia_campo_este"] = step_walk(1, 0, 600)
        # 4) Abrir barrera Hacienda como lo hace el gestor y volver a cruzar
        bar = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label() == "BAR_Hacienda")
        bar.set_actor_hidden_in_game(True); bar.set_actor_enable_collision(False)
        tp(-900, -1000); tests["barrera_hacienda_abierta"] = step_walk(-1, 0, 400)
        res["tests"] = tests
        # errores runtime del pawn en el log de PIE se revisan aparte
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))
