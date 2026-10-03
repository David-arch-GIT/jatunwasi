import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_bp.json"
res = {"componentes": [], "err": []}
PATH = "/Game/JWN/Blueprints/BP_CriaturaViva"
bp = unreal.EditorAssetLibrary.load_asset(PATH)
# componentes via subobject
try:
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    for h in handles:
        d = sds.k2_find_subobject_data_from_handle(h)
        obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if obj:
            res["componentes"].append(obj.get_name() + " (" + obj.get_class().get_name() + ")")
except Exception as e:
    res["err"].append("subobj:" + str(e)[:50])
# CDO: leer radios y defaults
try:
    cdo = unreal.get_default_object(bp.generated_class())
    res["radio_zona_var"] = cdo.get_editor_property("RadioZona")
    res["velmax_var"] = cdo.get_editor_property("VelMax")
    for comp in cdo.get_components_by_class(unreal.SphereComponent):
        res.setdefault("esferas_cdo", []).append(comp.get_name() + " r=" + str(comp.get_editor_property("sphere_radius")))
except Exception as e:
    res["err"].append("cdo:" + str(e)[:50])
open(OUT, "w").write(json.dumps(res, indent=1))
