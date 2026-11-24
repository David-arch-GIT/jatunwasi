import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
ns=unreal.NavigationSystemV1
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def nav(x,y,z):
    r=ns.project_point_to_navigation(w,unreal.Vector(x,y,z),None,None,unreal.Vector(180,180,500))
    return None if r is None else round(r.z)
R={"templo":[],"escalera":[]}
for y in [9600,10000,10400]: R["templo"].append({"y":y,"nav":nav(50,y,30)})
for (k,x,y,z) in [("base",-7450,-2800,80),("media",-7510,-2550,240),("alto",-7580,-2350,380),("corredor",-7150,-1770,440)]:
    R["escalera"].append({k:nav(x,y,z)})
open(out+"/verif_fix2.json","w").write(json.dumps(R)); print("V")
