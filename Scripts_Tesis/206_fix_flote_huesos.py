# 206_fix_flote_huesos.py - aterriza por el hueso mas bajo (ignora la Icosphere que contamina bounds)
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
        bones=smc.get_all_socket_names() if hasattr(smc,'get_all_socket_names') else []
        # mejor: nombres de huesos
        try:
            bnames=smc.get_editor_property("skeletal_mesh_asset").get_skeleton().get_reference_pose() # no sirve directo
        except Exception: pass
        # usar get_bone_name por indice
        names=[]
        try:
            n=smc.get_num_bones()
            for i in range(n): names.append(smc.get_bone_name(i))
        except Exception as e:
            R["err"].append("bones_%s:%s"%(lbl,str(e)[:30]))
        minz=1e9; minb=None
        for bn in names:
            try:
                wl=smc.get_bone_location(bn, unreal.ComponentType.WORLD) if hasattr(unreal,'ComponentType') else smc.get_bone_location(bn)
            except Exception:
                try: wl=smc.get_socket_location(bn)
                except Exception: continue
            if wl and wl.z<minz: minz=wl.z; minb=bn
        loc=a.get_actor_location()
        ground=gz(w,loc.x,loc.y)
        rel=smc.get_editor_property("relative_location")
        # offset para que el hueso mas bajo quede ~6cm sobre el piso (tobillo/dedo)
        corr=(ground+4.0)-minz
        newrelz=rel.z+corr
        smc.set_editor_property("relative_location", unreal.Vector(rel.x, rel.y, newrelz))
        R["fix"].append({"lbl":lbl,"min_bone":str(minb),"bone_z":round(minz,1),"ground":round(ground,1),
            "relz_antes":round(rel.z,1),"corr":round(corr,1),"relz_nuevo":round(newrelz,1),"nbones":len(names)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flote_huesos.json","w").write(json.dumps(R))
