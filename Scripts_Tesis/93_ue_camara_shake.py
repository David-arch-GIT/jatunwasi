# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Crea un asset de Camera Shake (CS_Aparicion) para el temblor de camara cuando aparece una leyenda.
#           LegacyCameraShake con oscilacion de rotacion (pitch/yaw/roll) y locacion, corto y fuerte.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/shake.json"
res = {"ok": False, "cls": None, "err": None}
try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    PATH = "/Game/JWN/Apariciones"
    NAME = "CS_Aparicion"
    if unreal.EditorAssetLibrary.does_asset_exist(PATH + "/" + NAME):
        unreal.EditorAssetLibrary.delete_asset(PATH + "/" + NAME)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.LegacyCameraShake)
    bp = tools.create_asset(NAME, PATH, None, factory)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    cdo.set_editor_property("oscillation_duration", 0.9)
    cdo.set_editor_property("oscillation_blend_in_time", 0.05)
    cdo.set_editor_property("oscillation_blend_out_time", 0.35)
    def setosc(struct_prop, comp, amp, freq):
        s = cdo.get_editor_property(struct_prop)
        o = s.get_editor_property(comp)
        o.set_editor_property("amplitude", amp)
        o.set_editor_property("frequency", freq)
        s.set_editor_property(comp, o)
        cdo.set_editor_property(struct_prop, s)
    # rotacion: sacude pitch/yaw fuerte, roll leve
    setosc("rot_oscillation", "pitch", 2.8, 32.0)
    setosc("rot_oscillation", "yaw", 2.2, 28.0)
    setosc("rot_oscillation", "roll", 1.6, 24.0)
    # locacion: leve zarandeo
    setosc("loc_oscillation", "x", 2.0, 20.0)
    setosc("loc_oscillation", "y", 2.0, 22.0)
    setosc("loc_oscillation", "z", 1.5, 18.0)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(PATH + "/" + NAME)
    res["ok"] = True
    res["cls"] = bp.generated_class().get_name()
except Exception as e:
    import traceback; res["err"] = traceback.format_exc()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("SHAKE done ok=%s" % res["ok"])
