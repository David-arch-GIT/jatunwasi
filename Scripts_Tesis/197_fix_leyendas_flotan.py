# 197_fix_leyendas_flotan.py (v2) - aterriza por los pies de la MALLA via bounds del asset
import unreal, json, traceback
R={"fix":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","PANEL","POSTE","MALEZA","RUTA","COL_"]
def groundz(w, x, y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return None
def mesh_bottom_world(smc):
    t=smc.get_world_transform()
    loc=t.translation; sc=t.scale3d
    mesh=smc.get_skeletal_mesh_asset()
    b=mesh.get_bounds()  # BoxSphereBounds local
    local_bottom=b.origin.z - b.box_extent.z
    return loc.z + local_bottom*sc.z
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende"]:
        a=None
        for x in eas.get_all_level_actors():
            if x.get_actor_label()==lbl: a=x; break
        if not a: R["err"].append("no_"+lbl); continue
        smc=a.get_component_by_class(unreal.SkeletalMeshComponent)
        loc=a.get_actor_location()
        mb=mesh_bottom_world(smc)
        gz=groundz(w, loc.x, loc.y)
        if gz is None: R["err"].append("noground_"+lbl); continue
        gap=mb-(gz-8.0)
        newz=loc.z-gap
        a.set_actor_location(unreal.Vector(loc.x,loc.y,newz), False, True)
        mb2=mesh_bottom_world(smc)
        R["fix"].append({"lbl":lbl,"gz":round(gz),"mb_antes":round(mb),"gap":round(gap),
            "newZ":round(newz),"mb_despues":round(mb2)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flotan.json","w").write(json.dumps(R))
