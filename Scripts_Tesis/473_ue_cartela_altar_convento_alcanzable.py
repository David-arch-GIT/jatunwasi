# 473_ue_cartela_altar_convento_alcanzable.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG: Cartela_altar_convento estaba DENTRO de la capilla (x>8000, sin NavMesh); el punto
#   caminable mas cercano (7930,5000) queda a 6 m y el BP_Cartela solo abre a < 4.5 m -> nunca se abria.
#   Se mueve la cartela hacia el umbral de la capilla, sobre el rayo visitante->altar, a ~2.2 m del punto
#   caminable (o 50 cm antes del primer obstaculo), z=150. Respaldo previo del mapa. Guarda.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cartela_altar.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_cartela_altar.umap")
    w = unreal.EditorLevelLibrary.get_editor_world()
    cart = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "Cartela_altar_convento"][0]
    O = unreal.Vector(7930, 5000, 160); A = unreal.Vector(8530, 5000, 150)
    h = unreal.SystemLibrary.line_trace_single(w, O, A, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [cart], unreal.DrawDebugTrace.NONE, True)
    t = h.to_tuple() if h else None
    lim = (t[3] - 50) if (t and t[0]) else 600
    res["obstaculo"] = [t[9].get_actor_label() if t and t[0] and t[9] else None, round(t[3]) if t and t[0] else None]
    d = max(120, min(220, lim))
    nuevo = unreal.Vector(O.x + d, 5000, 150)
    res["antes"] = [round(v) for v in (cart.get_actor_location().x, cart.get_actor_location().y, cart.get_actor_location().z)]
    cart.set_actor_location(nuevo, False, False)
    L = cart.get_actor_location(); res["despues"] = [round(L.x), round(L.y), round(L.z)]
    r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(7930, 5000, 60), None, None, unreal.Vector(5, 5, 150))
    p = r[0] if isinstance(r, tuple) else r
    res["dist_mano"] = round(math.dist([p.x, p.y, p.z + 120], [L.x, L.y, L.z]))
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
