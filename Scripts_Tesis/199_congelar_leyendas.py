# 199_congelar_leyendas.py
# Congela las 3 Cria: movimiento NONE + gravedad 0 + actor Z = piso + media-capsula
# -> el Character NO cae, NO snapea a colliders mas altos, NO se traslada por anim. Queda clavado al piso.
import unreal, json, traceback
R={"fix":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","PANEL","POSTE","MALEZA","RUTA","COL_"]
def groundz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return None
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende"]:
        a=None
        for x in eas.get_all_level_actors():
            if x.get_actor_label()==lbl: a=x; break
        if not a: R["err"].append("no_"+lbl); continue
        cap=a.get_component_by_class(unreal.CapsuleComponent)
        cmc=a.get_component_by_class(unreal.CharacterMovementComponent)
        hh=cap.get_scaled_capsule_half_height() if cap else 88.0
        loc=a.get_actor_location()
        gz=groundz(w, loc.x, loc.y)
        if gz is None: gz=-5.0
        newz=gz+hh-6.0  # base de capsula 6cm hundida en el piso
        a.set_actor_location(unreal.Vector(loc.x,loc.y,newz), False, True)
        done=[]
        if cmc:
            try: cmc.set_editor_property("gravity_scale", 0.0); done.append("grav0")
            except Exception as e: R["err"].append("g:"+str(e)[:25])
            try: cmc.set_editor_property("default_land_movement_mode", unreal.MovementMode.MOVE_NONE); done.append("moveNone")
            except Exception as e: R["err"].append("m:"+str(e)[:25])
            try: cmc.set_editor_property("max_walk_speed", 0.0); done.append("spd0")
            except Exception: pass
        a.set_actor_enable_collision(True)
        R["fix"].append({"lbl":lbl,"hh":round(hh),"gz":round(gz),"newZ":round(newz),"done":done})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/congelar.json","w").write(json.dumps(R))
