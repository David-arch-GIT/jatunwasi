# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Reemplaza las 4 apariciones estaticas App3D_* por SkeletalMeshActors animados en REPOSO (idle bucle).
#           Robusto: try/except por actor, siempre escribe JSON. Suelo por line trace con fallback.
# ------------------------------------------------------------
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar_reposo.json"
res = {"puestas": [], "err": [], "fatal": None}

MAP = {
 "App3D_Conv_Karisiri":  ("/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_full.karisiri_full",
                          "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Idle.karisiri_fullkarisiri_Idle"),
 "App3D_Conv_Condenado": ("/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_full.condenado_full",
                          "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Idle.condenado_fullcondenado_Idle"),
 "App3D_Hac_Duende":     ("/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_full.duende_full",
                          "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle"),
 "App3D_Plz_Duende":     ("/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_full.duende_full",
                          "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle"),
}

try:
    eas = unreal.EditorActorSubsystem()
    acts = eas.get_all_level_actors()
    by_label = {a.get_actor_label(): a for a in acts}
    world = unreal.EditorLevelLibrary.get_editor_world()

    def ground_z(x, y, z0):
        try:
            start = unreal.Vector(x, y, z0 + 500)
            end = unreal.Vector(x, y, z0 - 1000)
            hit = unreal.SystemLibrary.line_trace_single(
                world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [],
                unreal.DrawDebugTrace.NONE, True)
            if hit:
                return float(hit.impact_point.z)
        except Exception as e:
            res["err"].append("trace %s" % e)
        return None

    for label, (mesh_path, idle_path) in MAP.items():
        try:
            old = by_label.get(label)
            if old is None:
                res["err"].append("no encontrado: " + label); continue
            loc = old.get_actor_location(); rot = old.get_actor_rotation()
            skmesh = unreal.load_asset(mesh_path); idle = unreal.load_asset(idle_path)
            if skmesh is None or idle is None:
                res["err"].append("asset faltante: " + label); continue
            gz = ground_z(loc.x, loc.y, loc.z)
            z = gz if gz is not None else (loc.z - 80)
            newloc = unreal.Vector(loc.x, loc.y, z)
            a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, newloc, rot)
            a.set_actor_label(label.replace("App3D_", "AppSK_"))
            comp = a.skeletal_mesh_component
            try: comp.set_skeletal_mesh_asset(skmesh)
            except Exception: comp.set_skeletal_mesh(skmesh)
            comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            try:
                comp.set_animation(idle); comp.set_looping(True); comp.play(True)
            except Exception as e:
                res["err"].append("play %s: %s" % (label, e))
            try:
                ad = comp.get_editor_property("animation_data")
                ad.set_editor_property("anim_to_play", idle)
                ad.set_editor_property("looping", True)
                ad.set_editor_property("playing", True)
                comp.set_editor_property("animation_data", ad)
            except Exception as e:
                res["err"].append("animdata %s: %s" % (label, e))
            try: comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            except Exception: pass
            eas.destroy_actor(old)
            res["puestas"].append({"label": a.get_actor_label(),
                                   "loc": [round(newloc.x), round(newloc.y), round(newloc.z)], "gz": gz})
        except Exception as e:
            res["err"].append("%s: %s" % (label, e))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception as e:
    res["fatal"] = traceback.format_exc()

open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("REPOSO puestas=%d err=%d" % (len(res["puestas"]), len(res["err"])))
