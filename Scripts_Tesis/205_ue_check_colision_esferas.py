import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colision_esferas.json"
res = {"cdo": [], "instancias": [], "capsula": [], "err": []}
# CDO del BP
bp = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/BP_CriaturaViva")
cdo = unreal.get_default_object(bp.generated_class())
for c in cdo.get_components_by_class(unreal.SphereComponent):
    try:
        res["cdo"].append({
            "comp": c.get_name(),
            "radio": round(c.get_editor_property("sphere_radius")),
            "collision_enabled": str(c.get_collision_enabled()),
            "profile": str(c.get_collision_profile_name())
        })
    except Exception as e:
        res["err"].append("cdo:"+str(e)[:40])
# tambien la capsula
for c in cdo.get_components_by_class(unreal.CapsuleComponent):
    try:
        res["capsula"].append({"comp": c.get_name(), "radio": round(c.get_editor_property("capsule_radius")), "half_h": round(c.get_editor_property("capsule_half_height")), "collision": str(c.get_collision_enabled())})
    except Exception: pass
# instancias en el nivel
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if not a.get_actor_label().startswith("Cria_"): continue
    for c in a.get_components_by_class(unreal.SphereComponent):
        try:
            res["instancias"].append({"cria": a.get_actor_label(), "comp": c.get_name(), "radio": round(c.get_editor_property("sphere_radius")), "collision_enabled": str(c.get_collision_enabled()), "profile": str(c.get_collision_profile_name())})
        except Exception as e:
            res["err"].append("inst:"+str(e)[:30])
open(OUT, "w").write(json.dumps(res, indent=1))
