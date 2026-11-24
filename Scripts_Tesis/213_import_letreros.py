# 213_import_letreros.py - importa los 3 GLB de letrero y los coloca en las bocas de camino
import unreal, json, math, traceback
R={"placed":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","RUTA","COL_","Farol"]
def gz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-400),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return 12.0
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # borrar letreros viejos (cubos)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("Letrero_") or a.get_actor_label().startswith("LetreroM_"): eas.destroy_actor(a)
    plaza=(0.0,-1000.0)
    data={"HACIENDA":(-1150.0,-1000.0),"CONVENTO":(1250.0,-350.0),"TEMPLO":(0.0,150.0)}
    for nm,(sx,sy) in data.items():
        # importar GLB
        t=unreal.AssetImportTask()
        t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/sign_%s.glb"%nm)
        t.set_editor_property("destination_path","/Game/JWN/Letreros")
        t.set_editor_property("destination_name","SM_sign_%s"%nm)
        t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
        AT.import_asset_tasks([t])
        imp=t.get_editor_property("imported_object_paths")
        mesh=None
        for pth in imp:
            o=unreal.load_asset(pth)
            if isinstance(o, unreal.StaticMesh): mesh=o; break
        if not mesh:
            # buscar en la carpeta
            ar=unreal.AssetRegistryHelpers.get_asset_registry()
            for a in ar.get_assets_by_path(unreal.Name("/Game/JWN/Letreros"), recursive=True):
                if str(a.asset_class_path.asset_name)=="StaticMesh" and nm.lower() in str(a.asset_name).lower():
                    mesh=unreal.load_asset(str(a.package_name)); break
        if not mesh: R["err"].append("nomesh_%s imp=%s"%(nm,str(imp)[:80])); continue
        fz=gz(w,sx,sy)
        P=math.degrees(math.atan2(plaza[1]-sy, plaza[0]-sx))
        act=eas.spawn_actor_from_object(mesh, unreal.Vector(sx,sy,fz), unreal.Rotator(0.0,P-90.0,0.0))
        act.set_actor_label("LetreroM_%s"%nm)
        sm=act.get_component_by_class(unreal.StaticMeshComponent)
        sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        sm.set_editor_property("cast_shadow",False)
        R["placed"].append({"nm":nm,"fz":round(fz),"yaw":round(P-90)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_letreros.json","w").write(json.dumps(R))
