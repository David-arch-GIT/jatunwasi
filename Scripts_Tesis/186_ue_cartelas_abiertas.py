# Dejar las 19 cartelas ABIERTAS: panel visible + estado "Abierto"=True (fallback por tiempo).
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"n":0,"abierto_set":0,"detalle":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        cls=a.get_class().get_name()
        if "Cartela" in cls or a.get_actor_label().startswith("Cartela"):
            # panel visible
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                nm=c.get_name()
                if nm!="Colision":
                    try:
                        c.set_visibility(True, True); c.set_hidden_in_game(False, True)
                    except Exception: pass
            # variable Abierto = True (si existe)
            for var in ("Abierto","bAbierto","IsOpen","bIsOpen","Open"):
                try:
                    a.set_editor_property(var, True); R["abierto_set"]+=1; break
                except Exception: pass
            R["n"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open(out+"/cartelas_abiertas.json","w").write(json.dumps(R)); print("ABIERTAS", json.dumps({"n":R["n"],"abierto":R["abierto_set"]}))
