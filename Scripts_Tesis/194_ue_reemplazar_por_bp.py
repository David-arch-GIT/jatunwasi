# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-15
# Que hace: (UE) Reemplaza las 3 criaturas por instancias de BP_CriaturaViva en la MISMA XY y rotacion (Z al suelo).
#   Configura: CharacterMesh0 (mesh full + offset -halfheight + yaw -90 + Idle single-node loop), variables de instancia
#   (mesh/idle/walk/radio/velocidades/pausas). Borra los App_/AppSK_ de esas 3 criaturas. NO toca App_Plz_Duende.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reemplazo_bp.json"
res = {"creadas": [], "borradas": [], "err": []}
eas = unreal.EditorActorSubsystem()
ell = unreal.EditorLevelLibrary
w = ell.get_editor_world()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
BP = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/BP_CriaturaViva")
BPC = BP.generated_class()
# localizar mesh full e idle de cada criatura
def find_asset(cls, must):
    for a in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", cls), True):
        p = str(a.package_name); low = p.lower()
        if all(m in low for m in must):
            return unreal.EditorAssetLibrary.load_asset(p)
    return None
MESH = {
    "Karisiri": find_asset("SkeletalMesh", ["karisiri_full"]),
    "Condenado": find_asset("SkeletalMesh", ["condenado_full"]),
    "Duende": find_asset("SkeletalMesh", ["duende_full"]),
}
IDLE = {
    "Karisiri": find_asset("AnimSequence", ["karisiri", "idle"]),
    "Condenado": find_asset("AnimSequence", ["condenado", "idle"]),
    "Duende": find_asset("AnimSequence", ["duende", "idle"]),
}
WALK = {
    "Karisiri": find_asset("AnimSequence", ["karisiri", "walk"]),
    "Condenado": find_asset("AnimSequence", ["condenado", "walk"]),
    "Duende": find_asset("AnimSequence", ["duende", "walk"]),
}
# posicion actual de cada criatura = la del actor App_ correspondiente
APP = {"Karisiri": "App_Conv_Karisiri", "Condenado": "App_Conv_Condenado", "Duende": "App_Hac_Duende"}
pos = {}
for a in eas.get_all_level_actors():
    for cre, lab in APP.items():
        if a.get_actor_label() == lab:
            loc = a.get_actor_location(); rot = a.get_actor_rotation()
            pos[cre] = (loc.x, loc.y, loc.z, rot.yaw)
def suelo(x, y, z0):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,z0+200), unreal.Vector(x,y,z0-400), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]: return float(t[5].z)
    return z0
RADIO = {"Karisiri": 450.0, "Condenado": 450.0, "Duende": 550.0}
for cre in ["Karisiri", "Condenado", "Duende"]:
    if cre not in pos:
        res["err"].append("sin App_ pos: " + cre); continue
    x, y, z, yaw = pos[cre]
    gz = suelo(x, y, z)
    # spawn BP; capsula half height default 88
    a = ell.spawn_actor_from_class(BPC, unreal.Vector(x, y, gz + 88.0), unreal.Rotator(0.0, 0.0, yaw))
    a.set_actor_label("Cria_" + cre)
    # capsula real -> ajustar offset mesh
    cap = a.get_component_by_class(unreal.CapsuleComponent)
    hh = cap.get_editor_property("capsule_half_height") if cap else 88.0
    # mesh
    mc = a.get_component_by_class(unreal.SkeletalMeshComponent)
    try: mc.set_skeletal_mesh_asset(MESH[cre])
    except Exception:
        try: mc.set_editor_property("skeletal_mesh_asset", MESH[cre])
        except Exception as e: res["err"].append(cre+" mesh:"+str(e)[:30])
    mc.set_relative_location(unreal.Vector(0.0, 0.0, -hh), False, False)
    mc.set_relative_rotation(unreal.Rotator(0.0, 0.0, -90.0), False, False)
    # idle single-node loop (no hay ABP)
    try:
        mc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        spd = unreal.SingleAnimationPlayData()
        spd.set_editor_property("anim_to_play", IDLE[cre])
        spd.set_editor_property("saved_looping", True)
        spd.set_editor_property("saved_playing", True)
        mc.set_editor_property("animation_data", spd)
    except Exception as e:
        res["err"].append(cre+" idle:"+str(e)[:30])
    # variables de instancia
    for vn, vv in [("CriaturaMesh", MESH[cre]), ("IdleAnim", IDLE[cre]), ("WalkAnim", WALK[cre]),
                   ("RadioZona", RADIO[cre]), ("VelMin", 40.0), ("VelMax", 110.0), ("PausaMin", 2.0), ("PausaMax", 7.0), ("DistDeteccion", 350.0)]:
        try: a.set_editor_property(vn, vv)
        except Exception as e: res["err"].append("%s.%s:%s" % (cre, vn, str(e)[:24]))
    res["creadas"].append({"cre": cre, "loc": [round(x), round(y), round(gz+88)], "yaw": round(yaw,1),
                           "mesh": MESH[cre].get_name() if MESH[cre] else "NULL",
                           "idle": IDLE[cre].get_name() if IDLE[cre] else "NULL",
                           "walk": WALK[cre].get_name() if WALK[cre] else "NULL"})
# borrar App_ y AppSK_ de las 3 (no App_Plz_Duende)
BORRAR = ["App_Conv_Karisiri", "App_Conv_Condenado", "App_Hac_Duende",
          "AppSK_Conv_Karisiri", "AppSK_Conv_Condenado", "AppSK_Hac_Duende"]
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label() in BORRAR:
        try:
            eas.destroy_actor(a); res["borradas"].append(a.get_actor_label())
        except Exception as e:
            res["err"].append("del:"+str(e)[:30])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("REEMPLAZO creadas=%d borradas=%d" % (len(res["creadas"]), len(res["borradas"])))
