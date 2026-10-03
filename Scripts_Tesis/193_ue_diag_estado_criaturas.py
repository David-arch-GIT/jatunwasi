import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/estado_criaturas.json"
res = {"actores": [], "animbps": [], "nav_methods": [], "bp_autopossess": "?", "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not (lab.startswith("App_") or lab.startswith("AppSK_") or "CriaturaViva" in a.get_class().get_name()):
        continue
    loc = a.get_actor_location(); rot = a.get_actor_rotation()
    d = {"label": lab, "clase": a.get_class().get_name(),
         "loc": [round(loc.x), round(loc.y), round(loc.z)],
         "yaw": round(rot.yaw, 1)}
    try: d["hidden_editor"] = bool(a.is_temporarily_hidden_in_editor())
    except Exception: pass
    res["actores"].append(d)
# AnimBlueprints existentes
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for x in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "AnimBlueprint"), True):
    p = str(x.package_name)
    if p.startswith("/Game"):
        res["animbps"].append(p)
# metodos de NavigationSystemV1 (para reachability + rebuild)
res["nav_methods"] = [m for m in dir(unreal.NavigationSystemV1) if "random" in m.lower() or "reach" in m.lower() or "project" in m.lower() or "build" in m.lower()]
# auto possess del BP
try:
    bp = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/BP_CriaturaViva")
    cdo = unreal.get_default_object(bp.generated_class())
    res["bp_autopossess"] = str(cdo.get_editor_property("auto_possess_ai"))
    m = cdo.get_editor_property("mesh") if cdo.has_editor_property("mesh") else None
    res["bp_mesh_offset"] = str(m.get_editor_property("relative_location")) if m else "?"
except Exception as e:
    res["err"].append("bp:" + str(e)[:50])
open(OUT, "w").write(json.dumps(res, indent=1))
