# Test rapido: entender el retorno de project_point_to_navigation en puntos conocidos.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
ns=unreal.NavigationSystemV1
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
pts={"plaza":(0,-1000,100),"forest_conv":(9000,7000,100),"forest_hac":(-10000,-5000,100),
     "forest_tm":(1500,11000,100),"path_tm":(0,800,100),"far_out":(15000,15000,100)}
R={}
ext=unreal.Vector(600,600,500)
for k,(x,y,z) in pts.items():
    try:
        res=ns.project_point_to_navigation(w, unreal.Vector(x,y,z), None, None, ext)
        R[k]={"in":[x,y,z],"out":[round(res.x),round(res.y),round(res.z)]}
    except Exception as e:
        R[k]={"in":[x,y,z],"err":str(e)[:80]}
open(out+"/nav_proj_test.json","w").write(json.dumps(R,indent=1)); print("NAVTEST")
