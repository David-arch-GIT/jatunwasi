# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Crea actores StaticMeshActor propios (App3D_*) para las apariciones con el modelo 3D + material fantasmal (MI) + escala realista + apoyados en el piso (line trace). Oculta los BP_Apparition viejos (billboards) para no duplicar. No toca la estructura.
# Por que se necesito: El BP_Apparition revierte material/escala; se necesita control total del visual 3D.
# Resultado obtenido: (pendiente) apariciones 3D solidas colocadas.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar3d.json"
world = unreal.EditorLevelLibrary.get_editor_world()

CFG = {
    "Karisiri":  {"mesh": "/Game/JWN/Apariciones/karisiri_opt/StaticMeshes/karisiri_opt", "mi": "/Game/JWN/Apariciones/MI_App_Karisiri", "alt": 185.0, "gz": 20.0},
    "Condenado": {"mesh": "/Game/JWN/Apariciones/condenado_opt/StaticMeshes/condenado_opt", "mi": "/Game/JWN/Apariciones/MI_App_Condenado", "alt": 160.0, "gz": 20.0},
    "Duende":    {"mesh": "/Game/JWN/Apariciones/duende_color/StaticMeshes/duende_color", "mi": "/Game/JWN/Apariciones/MI_App_Duende", "alt": 150.0, "gz": 40.0},
}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

def mesh_h(sm):
    try:
        b = sm.get_bounding_box()
        return b.max.z - b.min.z
    except Exception:
        return 100.0

def ground_z(x, y, zref, fallback):
    start = unreal.Vector(x, y, zref + 200.0)
    end = unreal.Vector(x, y, zref - 400.0)
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, start, end,
              unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit and hit.blocking_hit:
            return hit.impact_point.z
    except Exception:
        pass
    return fallback

res = {"creados": [], "ocultos": []}

for a in list(all_actors()):
    if "Apparition" not in a.get_class().get_name():
        continue
    label = a.get_actor_label()
    key = None
    for k in CFG:
        if k.lower() in label.lower():
            key = k
            break
    if key is None:
        continue  # CarretaDelDiablo u otros: se dejan
    cfg = CFG[key]
    loc = a.get_actor_location()
    rot = a.get_actor_rotation()
    gz = ground_z(loc.x, loc.y, loc.z, cfg["gz"])
    sm = unreal.load_asset(cfg["mesh"])
    mi = unreal.load_asset(cfg["mi"])
    s = cfg["alt"] / max(1.0, mesh_h(sm))
    spawn_loc = unreal.Vector(loc.x, loc.y, gz)
    new = unreal.EditorLevelLibrary.spawn_actor_from_object(sm, spawn_loc, unreal.Rotator(0.0, rot.yaw, 0.0))
    new.set_actor_label("App3D_" + label.replace("App_", ""))
    new.set_actor_scale3d(unreal.Vector(s, s, s))
    smc = new.static_mesh_component if hasattr(new, "static_mesh_component") else new.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mi)
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    smc.set_editor_property("cast_shadow", False)
    try:
        smc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass
    res["creados"].append({"nuevo": new.get_actor_label(), "de": label, "escala": round(s, 3), "z": round(gz, 1),
                           "mat": [m.get_name() if m else None for m in smc.get_materials()]})
    # ocultar el billboard viejo
    try:
        a.set_editor_property("hidden", True)
        a.set_actor_hidden_in_game(True)
        res["ocultos"].append(label)
    except Exception as e:
        res.setdefault("ocultar_err", []).append(label + ":" + str(e))

try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    res["guardado"] = "ok"
except Exception as e:
    res["guardado"] = "err:" + str(e)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("COLOCAR3D: creados=%d" % len(res["creados"]))
