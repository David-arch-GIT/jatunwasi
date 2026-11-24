# FIX cartelas: que el rayo del control (LineTrace Visibility / 3DWidget) TOQUE la cartela
# aunque este cerrada. Pone colision de consulta + Block en Visibility y GameTraceChannel1
# en TODOS los componentes de cada cartela, SIN tocar la respuesta a Pawn (no romper overlap).
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"cartelas":[], "err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    VIS=unreal.CollisionChannel.ECC_VISIBILITY
    GT1=None
    try:
        GT1=unreal.CollisionChannel.ECC_3D_WIDGET
    except Exception: GT1=None
    BLK=unreal.CollisionResponseType.ECR_BLOCK
    for a in eas.get_all_level_actors():
        cls=a.get_class().get_name()
        if "Cartela" in cls or a.get_actor_label().startswith("Cartela"):
            comps=[]
            for c in a.get_components_by_class(unreal.PrimitiveComponent):
                try:
                    ce=c.get_collision_enabled()
                    if ce==unreal.CollisionEnabled.NO_COLLISION:
                        c.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
                    c.set_collision_response_to_channel(VIS, BLK)
                    if GT1 is not None: c.set_collision_response_to_channel(GT1, BLK)
                    comps.append(c.get_name())
                except Exception as e:
                    R["err"].append(a.get_actor_label()+":"+str(e)[:50])
            R["cartelas"].append({"lbl":a.get_actor_label(),"comps":comps})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True; R["n"]=len(R["cartelas"])
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open(out+"/fix_cartela_rayo.json","w").write(json.dumps(R)); print("FIXRAYO", json.dumps({"n":R.get("n"),"ok":R.get("ok")}))
