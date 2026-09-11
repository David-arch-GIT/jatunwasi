# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Pone a las 4 apariciones a CAMINAR en patrulla (InterpToMovement PING_PONG, auto-activo, lento),
#   SIN frenarse por colision (stop_on_collision=False -> nunca se atascan), visibles, con anim WALK, sin colision de actor.
#   Patrulla corta en direccion abierta (hacia el bosque) para no chocar estructuras.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/patrulla.json"
res = {"ok": [], "err": []}
# patrulla corta (dx,dy) direccion abierta + anim walk
CFG = {
 "AppSK_Conv_Condenado": {"off": (-350,-200), "walk": "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Walk.condenado_fullcondenado_Walk"},
 "AppSK_Conv_Karisiri":  {"off": (-300,-250), "walk": "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Walk.karisiri_fullkarisiri_Walk"},
 "AppSK_Hac_Duende":     {"off": (-400,-100), "walk": "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Walk.duende_fullduende_Walk"},
 "AppSK_Plz_Duende":     {"off": (300,-300),  "walk": "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Walk.duende_fullduende_Walk"},
}
eas = unreal.EditorActorSubsystem()
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for label, cfg in CFG.items():
    try:
        a = by.get(label)
        if a is None: res["err"].append("no " + label); continue
        off = cfg["off"]
        # mira hacia la direccion de caminata
        a.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=math.degrees(math.atan2(off[1], off[0])), roll=0.0), False)
        a.set_actor_hidden_in_game(False)
        # anim WALK
        comp = a.skeletal_mesh_component
        walk = unreal.load_asset(cfg["walk"])
        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", walk); ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", ad); comp.play(True)
        try: comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        except Exception: pass
        # InterpToMovement -> patrulla ping-pong sin frenar por colision
        itc = a.get_component_by_class(unreal.InterpToMovementComponent)
        if itc is None:
            sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            handles = sds.k2_gather_subobject_data_for_instance(a)
            sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.InterpToMovementComponent))
            itc = a.get_component_by_class(unreal.InterpToMovementComponent)
        def cp(x, y, z):
            c = unreal.InterpControlPoint()
            c.set_editor_property("position_control_point", unreal.Vector(x, y, z))
            c.set_editor_property("position_is_relative", True)
            return c
        itc.set_editor_property("control_points", [cp(0,0,0), cp(off[0], off[1], 0.0)])
        itc.set_editor_property("duration", 9.0)
        itc.set_editor_property("behaviour_type", unreal.InterpToBehaviourType.PING_PONG)
        itc.set_editor_property("auto_activate", True)
        for pk in ["stop_on_collision", "b_stop_on_collision"]:
            try: itc.set_editor_property(pk, False); break
            except Exception: pass
        for pk in ["force_sub_stepping", "b_force_sub_stepping"]:
            try: itc.set_editor_property(pk, False); break
            except Exception: pass
        res["ok"].append(label)
    except Exception as e:
        import traceback; res["err"].append("%s: %s" % (label, traceback.format_exc()))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PATRULLA done ok=%d err=%d" % (len(res["ok"]), len(res["err"])))
