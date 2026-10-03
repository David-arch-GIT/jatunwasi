import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_canasta.json"
res={"mercado":{}, "accion":None}
eas=unreal.EditorActorSubsystem()
byl={}
for a in eas.get_all_level_actors(): byl[a.get_actor_label()]=a
for nm in ["PLZP_CanastaPapa","PLZP_CanastaMaiz","PLZP_CanastaFruta","PLZP_CanastaChuno","PLZP_CanastaChuno_Fix"]:
    a=byl.get(nm)
    if a:
        l=a.get_actor_location(); res["mercado"][nm]=[round(l.x,1),round(l.y,1),round(l.z,1)]
# si Papa/Maiz/Fruta estan colocadas (no en origen), colocar Chuno cerca y ocultar la duplicada
refs=[res["mercado"].get(n) for n in ["PLZP_CanastaPapa","PLZP_CanastaMaiz","PLZP_CanastaFruta"] if res["mercado"].get(n) and (abs(res["mercado"][n][0])>50 or abs(res["mercado"][n][1])>50)]
if refs:
    # promedio de las referencias + offset
    ax=sum(r[0] for r in refs)/len(refs); ay=sum(r[1] for r in refs)/len(refs); az=refs[0][2]
    chuno=byl.get("PLZP_CanastaChuno_Fix") or byl.get("PLZP_CanastaChuno")
    dup=byl.get("PLZP_CanastaChuno") if chuno==byl.get("PLZP_CanastaChuno_Fix") else byl.get("PLZP_CanastaChuno_Fix")
    if chuno:
        chuno.set_actor_location(unreal.Vector(ax+45, ay+45, az), False, False)
        res["accion"]="movida a ("+str(round(ax+45))+","+str(round(ay+45))+","+str(round(az))+")"
    if dup:
        for c in dup.get_components_by_class(unreal.StaticMeshComponent): c.set_editor_property("hidden_in_game", True)
        res["dup_oculta"]=dup.get_actor_label()
else:
    res["accion"]="referencias tambien en origen; ocultando ambas Chuno"
    for nm in ["PLZP_CanastaChuno","PLZP_CanastaChuno_Fix"]:
        a=byl.get(nm)
        if a:
            for c in a.get_components_by_class(unreal.StaticMeshComponent): c.set_editor_property("hidden_in_game", True)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
