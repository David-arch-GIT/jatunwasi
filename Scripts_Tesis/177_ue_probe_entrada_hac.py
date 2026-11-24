import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ns=unreal.NavigationSystemV1
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
ext=unreal.Vector(250,250,500)
def top(x,y):
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,1200),unreal.Vector(x,y,-400),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    best=None
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
            # ignorar volumenes PCG flotantes
            if "PCG_" in n: continue
            if 0<=z<=120 and (best is None or z>best[0]): best=(z,n)
    return best
def nav(x,y,z=60):
    r=ns.project_point_to_navigation(w,unreal.Vector(x,y,z),None,None,ext)
    return None if r is None else round(r.z)
R={"eje_entrada":[]}
# eje desde el camino hacia el interior de la hacienda
pts=[(-6948,878),(-7050,650),(-7150,420),(-7250,180),(-7350,-60),(-7430,-300),
     (-7430,-500),(-7350,-750),(-7250,-1000),(-7150,-1250),(-7050,-1400)]
prev=None
for (x,y) in pts:
    f=top(x,y); n=nav(x,y)
    step=None
    if f and prev: step=abs(f[0]-prev)
    R["eje_entrada"].append({"xy":[x,y],"piso":f,"nav":n,"escalon_cm":step})
    if f: prev=f[0]
open(out+"/probe_entrada.json","w").write(json.dumps(R,indent=1)); print("ENTRADA")
