# 486_ue_test_adela_guia_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai APAGADO via 400) de Adela guia (UJWGuiaComponent). Fases:
#   "estado": DebugEstado + posiciones + VOCES que suenan a la vez (componentes con sonido SCL_Voz o la
#             voz de guia VozGuiaJW) + anim actual de la malla.
#   "seguir" + DIST: pone al visitante DIST cm DETRAS de Adela (segun su frente = yaw+90) sobre el NavMesh.
#   "tp" + TP=(x,y[,z]): pone al visitante en ese punto (NavMesh).
#   "mic" + ABIERTO=True/False: simula grip (ConvaiPlayer.bMute = not ABIERTO).
#   "forzar" + I: ForzarEstacion(I).
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "estado"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test486_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    cls = unreal.load_class(None, "/Script/JWGuia.JWGuiaComponent")
    acts = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    adela = [a for a in acts if a.get_actor_label() == "Adela_Convai"][0]
    comp = [c for c in adela.get_components_by_class(cls)][0]
    def nav(x, y, z=100):
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, z), None, None, unreal.Vector(150, 150, 600))
        return r[0] if isinstance(r, tuple) else r
    if PHASE == "seguir":
        L = adela.get_actor_location(); fy = math.radians(adela.get_actor_rotation().yaw + 90.0)
        q = nav(L.x - DIST * math.cos(fy), L.y - DIST * math.sin(fy), L.z + 50)
        if q: pawn.set_actor_location(unreal.Vector(q.x, q.y, q.z + 90), False, True)
    elif PHASE == "tp":
        q = nav(TP[0], TP[1], TP[2] if len(TP) > 2 else 100)
        if q: pawn.set_actor_location(unreal.Vector(q.x, q.y, q.z + 90), True, True)
        else: res["err"] = "sin navmesh"
    elif PHASE == "mic":
        for c in pawn.get_components_by_class(unreal.ActorComponent):
            if "ConvaiPlayer" in c.get_class().get_name():
                # NEVER = sin PostEditChange (si no, el editor reconstruye el pawn y el componente queda TRASH)
                c.set_editor_property("mute", not ABIERTO, unreal.PropertyAccessChangeNotifyMode.NEVER); res["mute"] = c.get_editor_property("mute")
    elif PHASE == "forzar":
        comp.forzar_estacion(I)
    res["t"] = round(unreal.GameplayStatics.get_time_seconds(world), 1)
    res["dbg"] = comp.debug_estado()
    A = adela.get_actor_location(); P = pawn.get_actor_location()
    res["adela"] = [round(A.x), round(A.y), round(A.z), round(adela.get_actor_rotation().yaw, 1)]
    res["pawn"] = [round(P.x), round(P.y), round(P.z)]
    res["dist"] = round(math.hypot(A.x - P.x, A.y - P.y))
    voces = []
    for a in acts:
        for c in a.get_components_by_class(unreal.AudioComponent):
            if not c.is_playing(): continue
            s = c.get_editor_property("sound")
            sc = None
            try: sc = s.get_editor_property("sound_class_object").get_name() if s and s.get_editor_property("sound_class_object") else None
            except Exception: pass
            if sc == "SCL_Voz" or c.get_name().startswith("VozGuiaJW"):
                voces.append([a.get_actor_label(), s.get_name() if s else None])
    res["voces"] = voces
    sk = adela.get_component_by_class(unreal.SkeletalMeshComponent)
    try:
        res["anim"] = sk.get_single_node_instance().get_animation_asset().get_name()
    except Exception:
        res["anim"] = "?"
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
