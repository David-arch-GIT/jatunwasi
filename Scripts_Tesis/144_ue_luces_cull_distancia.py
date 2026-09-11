# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) ANTI-SATURACION. Pone MaxDrawDistance a las 108 luces dinamicas locales (point/spot) para que solo
#   se rendericen cuando el jugador esta cerca (culling) -> en la plaza/nave/salon no se procesan todas a la vez.
#   Gran ahorro de GPU sin perder el look de cerca. Reversible. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luces_cull.json"
res = {"aplicadas": 0, "err": []}
eas = unreal.EditorActorSubsystem()
CULL = 1800.0   # cm: la luz se apaga a >18m (radio real es ~3m, asi que no se nota)
FADE = 400.0
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    if cn in ("PointLight", "SpotLight"):
        try:
            lc = a.get_component_by_class(unreal.LocalLightComponent)
            if not lc:
                lc = a.get_component_by_class(unreal.PointLightComponent)
            lc.set_editor_property("max_draw_distance", CULL)
            lc.set_editor_property("max_distance_fade_range", FADE)
            res["aplicadas"] += 1
        except Exception as e:
            res["err"].append(a.get_actor_label()+":"+str(e)[:50])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("LUCES CULL %d" % res["aplicadas"])
