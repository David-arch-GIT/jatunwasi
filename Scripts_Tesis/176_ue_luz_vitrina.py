# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Anade una luz PUNTUAL calida minima dentro de la vitrina del habito. Motivo: en Quest forward (sin GI)
#   el emissive NO ilumina objetos vecinos -> el habito quedaba negro. Luz: intensidad baja, radio corto, 3000K,
#   SIN sombras, con MaxDrawDistance (culada) = costo minimo. Label VIT_Habito_Luz. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luz_vitrina.json"
res = {"ok": [], "err": []}
ell = unreal.EditorLevelLibrary
X, Y, Z = 6120.0, 3650.0, 170.0
try:
    light = ell.spawn_actor_from_class(unreal.PointLight, unreal.Vector(X, Y, Z))
    light.set_actor_label("VIT_Habito_Luz")
    lc = light.get_component_by_class(unreal.PointLightComponent)
    lc.set_intensity(4.0)
    lc.set_editor_property("intensity_units", unreal.LightUnits.CANDELAS)
    lc.set_attenuation_radius(220.0)
    lc.set_editor_property("use_temperature", True)
    lc.set_editor_property("temperature", 3000.0)
    lc.set_cast_shadows(False)
    lc.set_editor_property("max_draw_distance", 1200.0)
    lc.set_editor_property("max_distance_fade_range", 300.0)
    lc.set_mobility(unreal.ComponentMobility.MOVABLE)
    res["ok"].append("luz creada 3000K int4 r220 sinSombra culada1200")
except Exception as e:
    res["err"].append(str(e)[:80])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("LUZ VITRINA ok")
