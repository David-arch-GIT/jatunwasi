# 501_ue_test_entrada_inyectada_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai apagado) FIEL AL VISOR de los controles: se inyecta la entrada en las
#   acciones de Enhanced Input (lo mismo que hace OpenXR en el Quest), NO en teclas:
#   "mover_ini" + VX,VY: inyeccion continua en IA_JW_Mover (palanca derecha empujada).
#   "mover_fin": detiene la inyeccion.   "leer": posicion del pawn + diagnostico de UJWEntradaVR.
#   "boton_a": inyecta IA_JW_BotonA (1 fotograma) -> debe alternar AmbienteApagado.
#   "pozo_apuntar": pone al pawn frente al pozo y apunta el control derecho.  "gatillo": inyecta IA_JW_Gatillo.
#   "estado": AmbienteApagado, PozoNarrado, visibilidad de la Moneda.
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "leer"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test501_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
    # el subsistema VIVO del jugador de PIE (hay restos de sesiones anteriores sin PlayerInput)
    sub = None
    imc = unreal.load_asset("/Game/XRFramework/Input/IMC_Default")
    for s in unreal.ObjectIterator(unreal.EnhancedInputLocalPlayerSubsystem):
        try:
            if s.get_player_input() is not None:
                sub = s
        except Exception:
            pass
    # En el visor BP_XRPawn.BeginPlay agrega IMC_Default (rama "HMD activo"); en PIE sin visor no -> se agrega aqui
    if sub is not None and not sub.has_mapping_context(imc):
        sub.add_mapping_context(imc, 0, unreal.ModifyContextOptions())
        res["imc_agregado_pie"] = True
    res["keys_mover"] = [str(k.get_editor_property("key_name")) for k in sub.query_keys_mapped_to_action(unreal.load_asset("/Game/JWN/Input/IA_JW_Mover"))] if sub else None
    res["sub_path"] = sub.get_path_name() if sub else None
    res["subsistema"] = bool(sub)
    def acc(n): return unreal.load_asset("/Game/JWN/Input/" + n)
    def valor(x, y, tipo):
        v = unreal.InputActionValue()
        nombre = {unreal.InputActionValueType.AXIS2D: "Axis2D", unreal.InputActionValueType.BOOLEAN: "Boolean"}[tipo]
        v.import_text("(Value=(X=%f,Y=%f,Z=0.000000),ValueType=%s)" % (x, y, nombre))
        res["valor_inyectado"] = unreal.EnhancedInputLibrary.conv_input_action_value_to_string(v)
        return v
    # Via C++ (UJWEntradaVR::PruebaInyectar*): mismo PlayerInput que la logica real + IMC_Default como en el visor
    if PHASE == "mover_vec":
        res["ok_iny"] = unreal.JWEntradaVR.prueba_inyectar(pawn, "Mover", unreal.Vector(VX, VY, 0.0))
    elif PHASE == "mover_cont":
        res["ok_iny"] = unreal.JWEntradaVR.prueba_inyectar_continuo(pawn, "Mover", unreal.Vector(VX, VY, 0.0), True)
    elif PHASE == "mover_stop":
        res["ok_iny"] = unreal.JWEntradaVR.prueba_inyectar_continuo(pawn, "Mover", unreal.Vector(0, 0, 0), False)
    elif PHASE == "boton_a_vec":
        res["ok_iny"] = unreal.JWEntradaVR.prueba_inyectar(pawn, "BotonA", unreal.Vector(1.0, 0.0, 0.0))
    elif PHASE == "gatillo_vec":
        res["ok_iny"] = unreal.JWEntradaVR.prueba_inyectar(pawn, "Gatillo", unreal.Vector(1.0, 0.0, 0.0))
    elif PHASE == "mover_ini":
        sub.start_continuous_input_injection_for_action(acc("IA_JW_Mover"), valor(VX, VY, unreal.InputActionValueType.AXIS2D), [], [])
    elif PHASE == "mover_fin":
        sub.stop_continuous_input_injection_for_action(acc("IA_JW_Mover"))
    elif PHASE == "boton_a":
        sub.inject_input_for_action(acc("IA_JW_BotonA"), valor(1.0, 0.0, unreal.InputActionValueType.BOOLEAN), [], [])
    elif PHASE == "gatillo":
        sub.inject_input_for_action(acc("IA_JW_Gatillo"), valor(1.0, 0.0, unreal.InputActionValueType.BOOLEAN), [], [])
    elif PHASE == "pozo_apuntar":
        pozo = [a for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if a.actor_has_tag("PozoDeseos")][0]
        P = pozo.get_actor_location()
        r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(P.x + 300, P.y, P.z), None, None, unreal.Vector(100, 100, 400))
        q = r[0] if isinstance(r, tuple) else r
        pawn.set_actor_location(unreal.Vector(q.x, q.y, q.z + 60), False, True)
        aim = [c for c in pawn.get_components_by_class(unreal.SceneComponent) if c.get_name().startswith("MotionControllerRightAim")][0]
        aim.set_world_rotation(unreal.MathLibrary.find_look_at_rotation(aim.get_world_location(), unreal.Vector(P.x, P.y, P.z + 40)), False, False)
    L = pawn.get_actor_location(); res["pawn"] = [round(L.x, 1), round(L.y, 1), round(L.z, 1)]
    res["diag"] = unreal.JWEntradaVR.diagnostico(pawn)
    for k in ("AmbienteApagado", "PozoNarrado"):
        try: res[k] = pawn.get_editor_property(k)
        except Exception: res[k] = "?"
    for c in pawn.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name().startswith("Moneda"):
            res["moneda_visible"] = c.is_visible(); M = c.get_world_location(); res["moneda"] = [round(M.x), round(M.y), round(M.z)]
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
