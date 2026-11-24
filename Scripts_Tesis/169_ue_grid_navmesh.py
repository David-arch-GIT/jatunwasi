# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: grilla de puntos sobre el mapa; para cada uno prueba si
#   es NAVEGABLE (project_point_to_navigation != None). Mapea la cobertura real del NavMesh
#   para detectar FUGA por teletransporte (NavMesh sobre piso de bosque).
# Resultado: Saved/ClaudeBackups/nav_grid.json  (lista de [x,y] navegables)
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
ns=unreal.NavigationSystemV1
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ext=unreal.Vector(490,490,600)
nav=[]; tested=0
x=-12000
while x<=11000:
    y=-7000
    while y<=18000:
        tested+=1
        try:
            res=ns.project_point_to_navigation(w, unreal.Vector(x,y,100), None, None, ext)
            if res is not None:
                nav.append([x,y,round(res.z)])
        except Exception:
            pass
        y+=1000
    x+=1000
open(out+"/nav_grid.json","w").write(json.dumps({"step":1000,"tested":tested,"nav":nav}))
print("NAVGRID_DONE", tested, "tested,", len(nav), "navegables")
