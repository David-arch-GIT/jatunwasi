# 526_ue_vals_solo_en_salon.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: la usuaria: "la musica del 2do piso de la hacienda es muy fuerte y choca con la planta baja".
#   AMB_SalaBaile estaba a z 848 (sobre el techo) con esfera 350 + caida 1400 -> se oia en toda la planta
#   baja, mezclado con AMB_Hacienda. Ahora: en el centro del salon (z 600), girado 12.1 grados como el
#   edificio, atenuacion CAJA del tamano del salon oeste (520 x 320 x 130) con caida corta de 200 cm,
#   volumen 0.70 -> 0.45. La cabeza en la planta baja (z ~220) queda fuera del alcance (borde inferior 470-200).
#   Respaldo del mapa. Guarda.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vals_526.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_vals.umap")
    def act(): return [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "AMB_SalaBaile"][0]
    a = act()
    a.set_actor_location(unreal.Vector(-8366, -1617, 600), False, False)
    r = unreal.Rotator(); r.yaw = 12.1; act().set_actor_rotation(r, False)
    ac = act().get_editor_property("audio_component")
    st = ac.get_editor_property("attenuation_overrides")
    st.set_editor_property("attenuation_shape", unreal.AttenuationShape.BOX)
    st.set_editor_property("attenuation_shape_extents", unreal.Vector(520, 320, 130))
    st.set_editor_property("falloff_distance", 200.0)
    ac.set_editor_property("attenuation_overrides", st)
    ac.set_editor_property("override_attenuation", True)
    ac.set_editor_property("volume_multiplier", 0.45)
    ac = act().get_editor_property("audio_component"); st = ac.get_editor_property("attenuation_overrides")
    L = act().get_actor_location()
    res["despues"] = {"loc": [round(L.x), round(L.y), round(L.z)], "yaw": round(act().get_actor_rotation().yaw, 1), "shape": str(st.get_editor_property("attenuation_shape")),
                      "ext": str(st.get_editor_property("attenuation_shape_extents")), "falloff": st.get_editor_property("falloff_distance"), "vol": ac.get_editor_property("volume_multiplier"), "override": ac.get_editor_property("override_attenuation")}
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
