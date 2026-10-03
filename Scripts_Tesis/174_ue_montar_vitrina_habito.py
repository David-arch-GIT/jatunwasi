# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) MONTA la vitrina del habito franciscano en el claustro (galeria tras la fila de arcos y=4100, entre
#   arcos x=5940 y x=6300 -> x=6120, contra el muro interior). Reusa VitrinaTall + maniqui_varon + M_JW_VitGlow.
#   Escala el habito 23x (7.5cm->~172cm, uniforme = sin deformar). Colisiones: vitrina BlockAll simple; maniqui+habito+
#   glow NO_COLLISION. Todo con label VIT_Habito_*. Guarda. (Posicion/rotacion se afina tras la captura.)
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/montaje_vitrina.json"
res = {"pasos": [], "err": []}
ell = unreal.EditorLevelLibrary
w = ell.get_editor_world()
X, Y = 6120.0, 3650.0
# 1) suelo real (trace desde z=250, bajo el piso superior)
gz = 15.0
r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(X, Y, 250), unreal.Vector(X, Y, -200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
if r:
    t = r.to_tuple()
    if t[0]:
        gz = float(t[5].z)
        res["suelo_z"] = round(gz); res["suelo_actor"] = str(t[9].get_actor_label()[:16]) if t[9] else "?"
res["pasos"].append("suelo z=%.0f" % gz)
def load(p): return unreal.EditorAssetLibrary.load_asset(p)
VIT = load("/Game/JWN/Props/Folklore/KitFolklore_SM_HF_VitrinaTall")
MAN = load("/Game/JWN/Props/Folklore/GLB/G_maniqui_varon/StaticMeshes/SM_maniqui_varon")
HAB = load("/Game/JWN/Props/Convento/HabitoFranciscano/vestimenta_y_habito_franciscano/StaticMeshes/vestimenta_y_habito_franciscano")
CUBE = load("/Engine/BasicShapes/Cube")
GLOW = load("/Game/JWN/Props/Materials/M_JW_VitGlow")
def spawn(obj, x, y, z, label):
    a = ell.spawn_actor_from_object(obj, unreal.Vector(x, y, z))
    a.set_actor_label(label)
    return a
def set_col(actor, profile, enabled):
    for c in actor.get_components_by_class(unreal.StaticMeshComponent):
        c.set_collision_profile_name(profile)
        c.set_collision_enabled(enabled)
# 2) vitrina (bloquea al jugador, colision simple)
try:
    vit = spawn(VIT, X, Y, gz, "VIT_Habito_Vitrina")
    set_col(vit, "BlockAll", unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    res["pasos"].append("vitrina OK")
except Exception as e: res["err"].append("vit:"+str(e)[:50])
# 3) maniqui dentro (sin colision)
try:
    man = spawn(MAN, X, Y, gz, "VIT_Habito_Maniqui")
    set_col(man, "NoCollision", unreal.CollisionEnabled.NO_COLLISION)
    res["pasos"].append("maniqui OK (170cm)")
except Exception as e: res["err"].append("man:"+str(e)[:50])
# 4) habito escalado 23x sobre el maniqui (sin colision)
try:
    hab = spawn(HAB, X, Y, gz, "VIT_Habito_Mesh")
    hab.set_actor_scale3d(unreal.Vector(23.0, 23.0, 23.0))
    set_col(hab, "NoCollision", unreal.CollisionEnabled.NO_COLLISION)
    # medir alto tras escalar
    b = hab.get_actor_bounds(False)
    res["habito_alto_cm"] = round(b[1].z * 2)
    res["pasos"].append("habito OK escala23")
except Exception as e: res["err"].append("hab:"+str(e)[:50])
# 5) tira glow calida en el techo interior de la vitrina (Opcion A, sin luz real)
try:
    glow = spawn(CUBE, X, Y, gz + 250, "VIT_Habito_Glow")
    glow.set_actor_scale3d(unreal.Vector(0.8, 0.5, 0.05))  # 80x50x5 cm
    gsmc = glow.get_component_by_class(unreal.StaticMeshComponent)
    if GLOW: gsmc.set_material(0, GLOW)
    gsmc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    try: gsmc.set_editor_property("cast_shadow", False)
    except Exception: pass
    res["pasos"].append("glow OK")
except Exception as e: res["err"].append("glow:"+str(e)[:50])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MONTAJE VITRINA pasos=%d err=%d" % (len(res["pasos"]), len(res["err"])))
