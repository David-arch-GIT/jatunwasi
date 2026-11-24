# 205_fix_flote_exacto.py - calcula el offset exacto de malla para clavar pies al piso (con MOVE_NONE el actor no snapea)
import unreal, json, traceback
R={"fix":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","RUTA","COL_"]
def gz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return -5.0
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende"]:
        a=None
        for x in eas.get_all_level_actors():
            if x.get_actor_label()==lbl: a=x; break
        if not a: R["err"].append("no_"+lbl); continue
        smc=a.get_component_by_class(unreal.SkeletalMeshComponent)
        mesh=smc.get_skeletal_mesh_asset()
        b=mesh.get_bounds()  # local BoxSphereBounds
        feet_local=b.origin.z - b.box_extent.z   # pies respecto al origen de malla
        t=smc.get_world_transform(); sc=t.scale3d.z
        relz=smc.get_editor_property("relative_location").z
        loc=a.get_actor_location()
        ground=gz(w,loc.x,loc.y)
        # con MOVE_NONE el actor se queda en loc.z. pies_mundo = loc.z + relz*? (rel es local, escala actor)
        # asumimos escala 1 en el actor; pies = loc.z + relz + feet_local*sc
        feet_now = loc.z + relz + feet_local*sc
        target = ground - 10.0
        corr = target - feet_now
        newrel = relz + corr
        rel=smc.get_editor_property("relative_location")
        smc.set_editor_property("relative_location", unreal.Vector(rel.x, rel.y, newrel))
        R["fix"].append({"lbl":lbl,"feet_local":round(feet_local,1),"scale":round(sc,2),
            "relz_antes":round(relz,1),"feet_now":round(feet_now,1),"ground":round(ground,1),
            "corr":round(corr,1),"relz_nuevo":round(newrel,1)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flote_exacto.json","w").write(json.dumps(R))
