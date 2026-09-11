# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Prepara el EVENTO de cada aparicion: la orienta hacia su punto de fuga (bosque), la deja OCULTA en juego,
#   le pone anim WALK, le agrega InterpToMovementComponent (ONE_SHOT, NO auto-activo) que la mueve hacia el bosque al activarse,
#   y crea una TriggerBox de proximidad en su sitio. NO toca materiales. Reporta.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/setup_eventos.json"
res = {"ok": [], "err": []}
# offset mundo (dx,dy) hacia el bosque (direccion inicial, ajustable)
CFG = {
 "AppSK_Conv_Condenado": {"off": (-700,-400), "walk": "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Walk.condenado_fullcondenado_Walk"},
 "AppSK_Conv_Karisiri":  {"off": (-600,-500), "walk": "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Walk.karisiri_fullkarisiri_Walk"},
 "AppSK_Hac_Duende":     {"off": (-800,-200), "walk": "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Walk.duende_fullduende_Walk"},
 "AppSK_Plz_Duende":     {"off": (600,-600),  "walk": "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Walk.duende_fullduende_Walk"},
}
eas = unreal.EditorActorSubsystem()
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for label, cfg in CFG.items():
    try:
        a = by.get(label)
        if a is None: res["err"].append("no " + label); continue
        off = cfg["off"]
        loc = a.get_actor_location()
        yaw = math.degrees(math.atan2(off[1], off[0]))
        a.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=yaw, roll=0.0), False)
        a.set_actor_hidden_in_game(True)
        # anim WALK
        comp = a.skeletal_mesh_component
        walk = unreal.load_asset(cfg["walk"])
        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", walk); ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", ad); comp.play(True)
        # InterpToMovementComponent (una vez, no auto-activo)
        itc = a.get_component_by_class(unreal.InterpToMovementComponent)
        if itc is None:
            handles = sds.k2_gather_subobject_data_for_instance(a)
            sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0], new_class=unreal.InterpToMovementComponent))
            itc = a.get_component_by_class(unreal.InterpToMovementComponent)
        def cp(x, y, z):
            c = unreal.InterpControlPoint()
            c.set_editor_property("position_control_point", unreal.Vector(x, y, z))
            c.set_editor_property("position_is_relative", True)
            return c
        itc.set_editor_property("control_points", [cp(0,0,0), cp(off[0], off[1], 0.0)])
        itc.set_editor_property("duration", 6.5)
        itc.set_editor_property("behaviour_type", unreal.InterpToBehaviourType.ONE_SHOT)
        itc.set_editor_property("auto_activate", False)
        # TriggerBox de proximidad en el sitio
        tbl = "Trig_" + label.replace("AppSK_", "")
        old = by.get(tbl)
        if old: eas.destroy_actor(old)
        tb = eas.spawn_actor_from_class(unreal.TriggerBox, unreal.Vector(loc.x, loc.y, loc.z + 90), unreal.Rotator())
        tb.set_actor_label(tbl)
        tb.set_actor_scale3d(unreal.Vector(15.0, 15.0, 9.0))
        res["ok"].append({"label": label, "yaw": round(yaw), "trigger": tbl})
    except Exception as e:
        import traceback; res["err"].append("%s: %s" % (label, traceback.format_exc()))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("SETUP EVENTOS done ok=%d err=%d" % (len(res["ok"]), len(res["err"])))
