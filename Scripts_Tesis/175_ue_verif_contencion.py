# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-09  VERIFICACION post-arreglo: NavMesh del bosque = 0, zonas siguen navegables.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
ns=unreal.NavigationSystemV1
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ext=unreal.Vector(300,300,500)
def navegable(x,y,z=100):
    try:
        r=ns.project_point_to_navigation(w, unreal.Vector(x,y,z), None, None, ext)
        return r is not None
    except Exception:
        return False
R={"deben_SI":{}, "deben_NO":{}, "grilla_bosque":{}}
# Zonas que DEBEN seguir navegables
si={"plaza":(0,-1000),"cam_cv":(4750,1960),"cam_tm":(0,3600),"cam_hc":(-4310,-143),
    "convento":(6200,5100),"templo":(0,14000),"hac_corredor":(-6600,-2200),"hac_patio":(-6900,-1350),
    "hac_sala_oeste":(-6000,-2500)}
for k,(x,y) in si.items(): R["deben_SI"][k]=navegable(x,y)
# Puntos de bosque que NO deben ser navegables
no={"bosque_conv":(9000,7000),"bosque_hac":(-10000,-5000),"bosque_tm":(1500,11000),
    "esquina":(-12000,-6000),"entre_conv":(3000,6000),"lejos_e":(8000,8000),"bosque_n":(-2000,10000)}
for k,(x,y) in no.items(): R["deben_NO"][k]=navegable(x,y)
# Grilla gruesa: contar navegables en bosque (lejos de zonas)
nav=0; tot=0
x=-12000
while x<=11000:
    y=-7000
    while y<=18000:
        tot+=1
        if navegable(x,y): nav+=1
        y+=1000
    x+=1000
R["grilla_bosque"]={"total":tot,"navegables":nav}
open(out+"/verif_contencion.json","w").write(json.dumps(R,indent=1)); print("VERIF", json.dumps({"SI":R["deben_SI"],"NO":R["deben_NO"],"grid":R["grilla_bosque"]}))
