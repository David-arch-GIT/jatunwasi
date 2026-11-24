# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-09  Precheck antes de excluir el terreno del NavMesh:
#  - lista actores de TERRENO (Ground_*/Landscape) con su tamano
#  - traza en plaza/caminos/escenarios para confirmar que tienen PISO PROPIO (malla separada
#    del terreno) -> si es asi, excluir el terreno del bosque es seguro.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
R={"terrenos":[], "traza":{}}
def top(x,y):
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    r=[]
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); r.append([round(t[5].z),(t[9].get_actor_label() if t[9] else "?")])
    return r
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label(); cls=a.get_class().get_name()
    if any(k in lbl for k in ["Ground_","Terrain","Landscape","Piso_General","Terreno"]) or cls=="Landscape":
        o,e=a.get_actor_bounds(False)
        R["terrenos"].append({"l":lbl,"cls":cls,"c":[round(o.x),round(o.y),round(o.z)],"ext":[round(e.x),round(e.y)]})
pts={"plaza":(0,-1000),"cam_cv":(4750,1960),"cam_tm":(0,3600),"cam_hc":(-4310,-143),
     "convento":(6200,5100),"templo":(0,14000),"hac_corredor":(-6600,-2200),"bosque_libre":(9000,7000)}
for k,(x,y) in pts.items():
    R["traza"][k]=top(x,y)
open(out+"/precheck_terreno.json","w").write(json.dumps(R,indent=1)); print("PRECHECK_DONE")
