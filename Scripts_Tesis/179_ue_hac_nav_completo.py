# Excluir props/muebles de la hacienda de la navegacion (mantienen colision) para que el
# NavMesh del PISO se genere completo -> la correa de navmesh permite caminar en todo el interior.
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"excluidos":0}
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    pref=("MUS_","BALL_","COR_","HACF_","HACD_","HACP_","NAT_","VitTall","Mani","MUS")
    for a in eas.get_all_level_actors():
        lbl=a.get_actor_label()
        l=a.get_actor_location()
        inhac = (-9200<=l.x<=-4900) and (-4000<=l.y<=-500)
        if inhac and lbl.startswith(pref):
            ch=False
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                c.set_editor_property("can_ever_affect_navigation", False); ch=True
            if ch: R["excluidos"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    R["ok"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open(out+"/hac_nav_completo.json","w").write(json.dumps(R)); print("HACNAV", json.dumps(R))
