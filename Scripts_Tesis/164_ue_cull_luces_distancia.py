# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08
# Que hace: pone DISTANCIA MAXIMA DE DIBUJO a todas las luces dinamicas (point/spot).
#   La luz ya aporta 0 mas alla de su attenuation_radius (~2.5-3.2m), asi que cullearla
#   a ~15-35m NO cambia nada visible, pero el motor deja de renderizarla cuando estas
#   lejos (otra zona) -> muchas menos luces por frame = mas margen GPU/termico para
#   transmitir. Con fade suave para que no haya pop. REVERSIBLE (max_draw_distance=0).
# Resultado: Saved/ClaudeBackups/cull_luces.json
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"cambiadas":0,"por_clase":{},"err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LocalLightComponent):  # point+spot (no directional)
            cls=c.get_class().get_name()
            try:
                r=float(c.get_editor_property("attenuation_radius"))
                dd=min(3500.0, max(1500.0, r*6.0))
                c.set_editor_property("max_draw_distance", dd)
                c.set_editor_property("max_distance_fade_range", max(200.0, r*1.0))
                R["cambiadas"]+=1
                R["por_clase"][cls]=R["por_clase"].get(cls,0)+1
            except Exception as e:
                R["err"].append(a.get_actor_label()+":"+str(e)[:50])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["saved"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/cull_luces.json","w").write(json.dumps(R)); print("CULL", json.dumps({k:R[k] for k in R if k!='err'}))
