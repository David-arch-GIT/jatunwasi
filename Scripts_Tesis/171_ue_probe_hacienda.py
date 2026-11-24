# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  PROBE hacienda (contencion). Multi-trace WorldStatic (complex) hacia
#  abajo = perfil vertical de superficies. Detecta: piso planta baja (~z58) presente o HUECO
#  (cae a terreno ~z0), escalera y 2o piso. + colision de actores clave.
# Resultado: Saved/ClaudeBackups/probe_hac.json
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]  # WorldStatic
R={"colision":{}, "piso_grid":[], "puntos":{}}
def stack(x,y,z0=1500,z1=-600):
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(
        w, unreal.Vector(x,y,z0), unreal.Vector(x,y,z1), WS, True, [],
        unreal.DrawDebugTrace.NONE, True)
    res=[]
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); ip=t[5]; ha=t[9]
            nm=ha.get_actor_label() if ha else "?"
            res.append((round(ip.z), nm))
    return res
# A) colision clave
keys=["HACV7_EXP_Foundation_Floors","COL_Rampa_Entrada","COL_Puente_Escalera2P",
      "COL_HACV7_StairRamp","HACV7_EXP_Staircase"]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl in keys or any(k in lbl for k in ["Door","Puerta","Entrada_","Staircase","Foundation"]):
        cs=a.get_components_by_class(unreal.StaticMeshComponent)
        info={}
        if cs:
            c=cs[0]
            try:
                info["enabled"]=str(c.get_collision_enabled()).split('.')[-1].rstrip('>')
                info["perfil"]=str(c.get_collision_profile_name())
                info["resp_pawn"]=str(c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)).split('.')[-1].rstrip('>')
                info["hidden"]=a.get_actor_hidden_in_game()
            except Exception as e: info["err"]=str(e)[:50]
        R["colision"][lbl]=info
# B) grilla piso planta baja: busca superficie en [20,160] (piso ~58) y la mas baja (terreno)
x=-8500
while x<=-5500:
    y=-3400
    while y<=-900:
        st=stack(x,y)
        floor=next(((z,n) for (z,n) in st if 20<=z<=160), None)
        low=st[-1] if st else None
        R["piso_grid"].append({"xy":[x,y],"floor":floor,"low":low,"nhits":len(st)})
        y+=600
    x+=600
# C) puntos especificos (stack completo)
pts={"entrada_rampa":(-7085,-620),"puerta_zona":(-5600,-1200),
     "escalera_abajo":(-7450,-2750),"escalera_media":(-7500,-2450),
     "escalera_bridge_2p":(-7590,-2300),"corredor_2p":(-7150,-1770),
     "sala_2p_oeste":(-8200,-1600)}
for k,(x,y) in pts.items():
    R["puntos"][k]=stack(x,y)
open(out+"/probe_hac.json","w").write(json.dumps(R,indent=1))
print("PROBE_HAC_DONE")
