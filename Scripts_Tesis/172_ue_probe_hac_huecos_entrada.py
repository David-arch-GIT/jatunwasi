# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Caracteriza los HUECOS de piso (franja norte) y la ENTRADA/puerta.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
R={"entrada":{}, "huecos_grid":[]}
def stack(x,y,z0=1500,z1=-600):
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,z0),unreal.Vector(x,y,z1),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    out2=[]
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); out2.append([round(t[5].z), (t[9].get_actor_label() if t[9] else "?")])
    return out2
# ENTRADA: actores clave
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl in ("COL_Rampa_Entrada","HACV7_EntranceApron_Final","TRG_HaciendaDoor") or ("Door" in lbl and "HAC" in lbl) or "EntranceApron" in lbl or "Rampa_Entrada" in lbl:
        o,e=a.get_actor_bounds(False)
        d={"cls":a.get_class().get_name(),"c":[round(o.x),round(o.y),round(o.z)],"ext":[round(e.x),round(e.y),round(e.z)]}
        cs=a.get_components_by_class(unreal.StaticMeshComponent)
        if cs:
            c=cs[0]
            d["enabled"]=str(c.get_collision_enabled()).split('.')[-1]
            d["perfil"]=str(c.get_collision_profile_name())
        R["entrada"][lbl]=d
# HUECOS: grilla fina franja norte
x=-8600
while x<=-5200:
    y=-1900
    while y<=-600:
        st=stack(x,y)
        has_floor=any(20<=z<=160 for z,_ in st)
        R["huecos_grid"].append({"xy":[x,y],"floor":has_floor,"stack":st})
        y+=350
    x+=400
open(out+"/hac_huecos.json","w").write(json.dumps(R))
print("HUECOS_DONE")
