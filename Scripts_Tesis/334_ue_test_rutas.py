# Prueba si existe RUTA de navegacion entre pares de puntos (lo que valida el teletransporte).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test_rutas.json"
res={"rutas":{}}
world=unreal.EditorLevelLibrary.get_editor_world()
def V(t): return unreal.Vector(t[0],t[1],t[2])
def ruta(a,b):
    try:
        path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world, V(a), V(b))
        if not path:
            return {"valida":False,"motivo":"no path obj"}
        pts=path.get_editor_property("path_points") if hasattr(path,"get_editor_property") else None
        try: valid=path.is_valid()
        except Exception: valid=None
        try: partial=path.is_partial()
        except Exception: partial=None
        try: unreach=path.is_unreachable()
        except Exception: unreach=None
        npts=len(pts) if pts else 0
        endd=None
        if pts and npts>0:
            last=pts[npts-1]
            endd=round(((last.x-b[0])**2+(last.y-b[1])**2+(last.z-b[2])**2)**0.5)
        return {"valida":valid,"parcial":partial,"inalcanzable":unreach,"n_puntos":npts,"dist_al_destino":endd}
    except Exception as e:
        return {"err":str(e)[:80]}
PARES={
 "HAC_ground->2P_landing":[(-7000,-2500,100),(-7588,-2478,450)],
 "HAC_ground->2P_bridge":[(-7000,-2500,100),(-7545,-2100,421)],
 "PATH_end->HAC_ground":[(-6948,878,60),(-7000,-2500,100)],
 "PLAZA->HAC_ground":[(0,-1000,80),(-7000,-2500,100)],
 "SPAWN->HAC_2P":[(-6200,-2500,205),(-7588,-2478,450)],
 "CONV_center->out_West":[(6290,5000,30),(5200,5000,30)],
 "CONV_center->out_East":[(6290,5000,30),(7350,5000,30)],
 "CONV_out_W->out_E(cruzar)":[(5200,5000,30),(7350,5000,30)],
}
for k,(a,b) in PARES.items():
    res["rutas"][k]=ruta(a,b)
open(OUT,"w").write(json.dumps(res,indent=1))
