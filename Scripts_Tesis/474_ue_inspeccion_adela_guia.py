# 474_ue_inspeccion_adela_guia.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) datos para programar a Adela como guia que acompana:
#   componentes de BP_GuiaInteractiva (clase, transform relativo, colision, malla/anim), animaciones de
#   /Game/JWN/Characters/AdelaFinal (duracion, desplazamiento de raiz/pelvis = camina en el sitio o no),
#   velocidad de locomocion del pawn (variables numericas del BP_XRPawn) y el actor Adela_Convai.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspeccion_adela.json"
res = {"err": None, "comps": [], "anims": {}, "pawn_vars": {}}
try:
    bp = unreal.load_asset("/Game/JWN/Blueprints/BP_GuiaInteractiva")
    res["parent"] = "?"
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
        if not o: continue
        d = {"name": o.get_name(), "cls": o.get_class().get_name()}
        if isinstance(o, unreal.SceneComponent):
            d["rel_loc"] = str(o.get_editor_property("relative_location")); d["rel_rot"] = str(o.get_editor_property("relative_rotation")); d["rel_scale"] = str(o.get_editor_property("relative_scale3d"))
        if isinstance(o, unreal.PrimitiveComponent):
            try: d["col_profile"] = str(o.get_collision_profile_name()); d["col_enabled"] = str(o.get_collision_enabled())
            except Exception: pass
        if isinstance(o, unreal.SkeletalMeshComponent):
            try: d["mesh"] = o.get_editor_property("skeletal_mesh_asset").get_path_name()
            except Exception: pass
            d["anim_mode"] = str(o.get_editor_property("animation_mode"))
        if isinstance(o, unreal.ShapeComponent) and hasattr(o, "get_unscaled_sphere_radius"):
            d["radio"] = o.get_unscaled_sphere_radius()
        res["comps"].append(d)
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in ar.get_assets_by_path("/Game/JWN/Characters/AdelaFinal", True):
        if str(ad.asset_class_path.asset_name) != "AnimSequence": continue
        a = ad.get_asset(); L = a.get_play_length()
        info = {"dur": round(L, 2), "root_motion": a.get_editor_property("enable_root_motion")}
        for b in ("root", "pelvis"):
            try:
                p0 = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, 0.0, False).translation
                p1 = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, L * 0.999, False).translation
                info[b] = [round(p1.x - p0.x, 1), round(p1.y - p0.y, 1), round(p1.z - p0.z, 1)]
            except Exception as e:
                info[b] = "err"
        res["anims"][str(ad.asset_name)] = info
    pbp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    cdo = unreal.get_default_object(unreal.load_object(None, "/Game/XRFramework/Blueprints/BP_XRPawn.BP_XRPawn_C"))
    for k in dir(cdo):
        pass
    for name in ("VelocidadMov", "Velocidad", "MoveSpeed", "Speed", "VelocidadMovimiento", "PasoCm", "MovSpeed"):
        try: res["pawn_vars"][name] = cdo.get_editor_property(name)
        except Exception: pass
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "Adela_Convai":
            R = a.get_actor_rotation(); res["adela_rot"] = [R.pitch, R.yaw, R.roll]; res["adela_scale"] = str(a.get_actor_scale3d())
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1, default=str))
