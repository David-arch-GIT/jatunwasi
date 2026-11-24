# 512_ue_tapar_puertas_2p.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: pedido de la usuaria: "en el 2do piso hay muchas puertas pero solo se entra por la de la
#   cortina; arreglalo o tapalo". Medido con 509/510/511 + escaneo fino (trazas complejas cada 5 cm):
#   - muro SUR (galeria -> salon, cara galeria ly 772, cara salon ly 828, grosor 56): vanos ABIERTOS en
#     lx -625..-430 (doble), -355..-245, 145..260, 645..760, 1165..1280 que no llevan a ningun lado;
#     el vano lx -855..-745 es el de la CORTINA (unica entrada al salon / final) -> se deja libre.
#   - muro NORTE (cara salon ly 1473): 4 hojas oscuras de 103 cm en vanos de ~112 cm -> rendija al vacio.
#   Arreglo: puertas cerradas SM_PuertaHacienda (Tripo, ya usadas en la Hacienda) con escala UNIFORME,
#   centradas en el grosor del muro sur; en el norte, una hoja detras de la existente que tapa la rendija.
#   Sin colision (los muros ya bloquean; no altera el NavMesh) y sin sombra (Quest). Respaldo del mapa.
#   Coordenadas locales del edificio: girado 12.1 grados en torno a (-7000,-2500). Piso alto z 432.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/tapar_2p.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None, "puestas": []}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_tapar2p.umap")
    O = (-7000.0, -2500.0); YAW = 12.1; A = math.radians(YAW); c, s = math.cos(A), math.sin(A)
    def mundo(lx, ly, z): return unreal.Vector(O[0] + lx * c - ly * s, O[1] + lx * s + ly * c, z)
    IZQ = unreal.load_asset("/Game/JWN/Puertas/SM_PuertaHacienda_HojaIzq")   # X 0..121 desde el pivote
    DER = unreal.load_asset("/Game/JWN/Puertas/SM_PuertaHacienda_HojaDer")   # X -117..0 desde el pivote
    Z = 432.0
    # borrar colocaciones previas de este script (re-ejecutable)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("PUERTA2P_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    def poner(nombre, malla, lx_pivote, ly_centro, esc):
        grosor = 10.0 * esc
        p = mundo(lx_pivote, ly_centro - grosor / 2.0, Z)
        a = unreal.EditorLevelLibrary.spawn_actor_from_object(malla, p)
        r = unreal.Rotator(); r.yaw = YAW; a.set_actor_rotation(r, False)
        a.set_actor_scale3d(unreal.Vector(esc, esc, esc))
        a.set_actor_label(nombre); a.set_folder_path("Hacienda/Puertas2P")
        smc = a.static_mesh_component
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        smc.set_editor_property("cast_shadow", False)
        smc.set_editor_property("can_ever_affect_navigation", False)
        L = a.get_actor_location()
        res["puestas"].append([nombre, malla.get_name(), esc, [round(L.x), round(L.y), round(L.z)]])
    LY_S = 800.0   # centro del muro sur
    # vanos simples del sur (~110-115 cm): una hoja izquierda centrada, esc 0.93 -> 112.5 x 250 (7 cm dentro del dintel)
    e1 = 0.93; w1 = 121.0 * e1
    for i, (a0, a1) in enumerate(((-355, -245), (145, 260), (645, 760), (1165, 1280))):
        cx = (a0 + a1) / 2.0
        poner("PUERTA2P_S_%d" % (i + 1), IZQ, cx - w1 / 2.0, LY_S, e1)
    # vano doble del sur (lx -625..-430, ~195 cm): dos hojas esc 0.90 (109+106 = 215, bordes dentro de las jambas)
    e2 = 0.90; cx = (-625 - 430) / 2.0
    poner("PUERTA2P_S_doble_izq", IZQ, cx - 121.0 * e2, LY_S, e2)
    poner("PUERTA2P_S_doble_der", DER, cx + 117.0 * e2, LY_S, e2)
    # norte: hoja detras de la existente (cara salon 1473, hoja existente en ly ~1531) -> ly 1545
    e3 = 0.90; w3 = 121.0 * e3
    for i, (a0, a1) in enumerate(((-875, -765), (-335, -225), (205, 320), (705, 820))):
        cx = (a0 + a1) / 2.0
        poner("PUERTA2P_N_%d" % (i + 1), IZQ, cx - w3 / 2.0, 1545.0, e3)
    res["guardado"] = False   # se guarda solo tras verificar las capturas (regla del proyecto)
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
