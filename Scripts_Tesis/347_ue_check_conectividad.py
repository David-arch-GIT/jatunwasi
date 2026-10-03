# Verifica CONEXION (ruta) entre puntos clave tras el rebuild. Parcial=cortado, completo=conecta.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/conectividad.json"
res={"rutas":{}}
world=unreal.EditorLevelLibrary.get_editor_world()
def V(t): return unreal.Vector(t[0],t[1],t[2])
def ruta(a,b):
    try:
        p=unreal.NavigationSystemV1.find_path_to_location_synchronously(world, V(a), V(b))
        if not p: return {"valida":False}
        try: valida=p.is_valid()
        except Exception: valida=None
        try: parcial=p.is_partial()
        except Exception: parcial=None
        pts=p.get_editor_property("path_points")
        endd=None
        if pts and len(pts)>0:
            last=pts[len(pts)-1]
            endd=round(((last.x-b[0])**2+(last.y-b[1])**2+(last.z-b[2])**2)**0.5)
        return {"valida":valida,"parcial":parcial,"n":len(pts) if pts else 0,"dist_destino":endd}
    except Exception as e:
        return {"err":str(e)[:60]}
PARES={
 "escalera_SUBIR(abajo->2P)":[(-6930,-2320,60),(-7545,-2100,435)],
 "escalera_SUBIR(abajo->landing)":[(-6930,-2320,60),(-7588,-2478,450)],
 "entrada(calle->hacienda)":[(-7300,-300,60),(-7000,-2400,60)],
 "convento_CRUZAR(afueraW->afueraE)":[(5200,5000,30),(7350,5000,30)],
 "convento(centro->afueraW)":[(6290,5000,30),(5200,5000,30)],
}
for k,(a,b) in PARES.items():
    res["rutas"][k]=ruta(a,b)
open(OUT,"w").write(json.dumps(res,indent=1))
