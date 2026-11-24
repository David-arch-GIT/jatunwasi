# 196_fix_hacienda_cull.py - revisa/arregla cull del edificio hacienda (EXP_) y StaticMeshActors de zona
import unreal, json, traceback
R={"checked":[], "fixed":0, "err":[]}
def zone(x,y):
    if -8800<x<-5600 and -3800<y<-1300: return "HAC"
    if 4800<x<7400 and 3000<y<5400: return "CONV"
    return None
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        lbl=a.get_actor_label()
        if a.get_class().get_name()!="StaticMeshActor": continue
        if lbl.startswith(("PCG_","MALEZA_","RUTA_","COL_")): continue
        loc=a.get_actor_location()
        z=zone(loc.x,loc.y)
        if not z: continue
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                ld=c.get_editor_property("ld_max_draw_distance")
                cached=c.get_editor_property("cached_max_draw_distance")
                if (ld and ld>0 and ld<15000):
                    if len(R["checked"])<12: R["checked"].append("%s|%s ld=%s cached=%s"%(lbl,c.get_name(),round(ld),round(cached)))
                    c.set_editor_property("ld_max_draw_distance", 0.0)  # sin recorte (edificio siempre visible)
                    R["fixed"]+=1
            except Exception as e:
                R["err"].append(str(e)[:40])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hacull.json","w").write(json.dumps(R))
