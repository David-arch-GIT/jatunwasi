# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: detalle de movilidad/intensidad/radio de todas las luces
# (solo lectura) para decidir si son dinamicas (coste) o estaticas/horneadas.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
R={"by_mobility":{},"sample":[],"spot_sample":[],"dir":[]}
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.LightComponent):
        cls=c.get_class().get_name()
        try: mob=str(c.get_editor_property("mobility"))
        except Exception: mob="err"
        key=cls+"|"+mob
        R["by_mobility"][key]=R["by_mobility"].get(key,0)+1
        if cls=="PointLightComponent" and len(R["sample"])<8:
            try:
                R["sample"].append({"lbl":a.get_actor_label(),"mob":mob,
                  "intensity":round(c.get_editor_property("intensity"),1),
                  "radius":round(c.get_editor_property("attenuation_radius"),0)})
            except Exception as e: R["sample"].append({"lbl":a.get_actor_label(),"err":str(e)[:60]})
        if cls=="SpotLightComponent" and len(R["spot_sample"])<6:
            try: R["spot_sample"].append({"lbl":a.get_actor_label(),"mob":mob,"intensity":round(c.get_editor_property("intensity"),1)})
            except Exception: pass
        if cls=="DirectionalLightComponent":
            try: R["dir"].append({"lbl":a.get_actor_label(),"mob":mob,"intensity":round(c.get_editor_property("intensity"),2)})
            except Exception: pass
open(out+"/lights_detail.json","w").write(json.dumps(R,indent=1))
print("LIGHTS_DONE")
