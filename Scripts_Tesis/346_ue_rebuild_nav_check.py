# Dispara RebuildNavigation y (segun 'fase') verifica cobertura en escaleras/arcos/entrada.
import unreal, json, sys
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rebuild_nav_check.json"
fase = globals().get("FASE","trigger")
world=unreal.EditorLevelLibrary.get_editor_world()
res={"fase":fase}
if fase=="trigger":
    unreal.SystemLibrary.execute_console_command(world, "RebuildNavigation")
    res["msg"]="RebuildNavigation lanzado"
else:
    def nav(x,y,z):
        try:
            loc=unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x,y,z), None, None, unreal.Vector(250,250,700))
            d=((loc.x-x)**2+(loc.y-y)**2+(loc.z-z)**2)**0.5
            return {"nav":(not(abs(loc.x)<0.1 and abs(loc.y)<0.1) and d<900),"proj_z":round(loc.z),"dist":round(d)}
        except Exception as e:
            return {"err":str(e)[:40]}
    res["puntos"]={
     "escalera_abajo":nav(-6930,-2320,60),
     "escalera_rellano_2P":nav(-7545,-2100,435),
     "escalera_landing":nav(-7588,-2478,435),
     "entrada_alfombra":nav(-7285,-1153,60),
     "entrada_medio":nav(-7300,-800,60),
     "conv_centro":nav(6290,5000,30),
     "conv_arco_W":nav(5550,5000,30),
     "conv_afuera_W":nav(5200,5000,30),
    }
open(OUT,"w").write(json.dumps(res,indent=1))
