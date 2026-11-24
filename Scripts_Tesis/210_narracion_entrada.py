# 210_narracion_entrada.py - 4 cartelas de RELATO en las entradas (voz + texto en la vista por proximidad)
import unreal, json, traceback
R={"placed":[], "robust":0, "err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    bpclass=unreal.EditorAssetLibrary.load_blueprint_class("/Game/Cartelas/BP_Cartela")
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    def gz(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-400),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
                if any(k in n for k in ["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","RUTA","COL_","Farol","Cartela"]): continue
                return z
        return 12.0
    zonas={"plaza":(600,-520),"hacienda":(-7250,-820),"convento":(5950,4250),"templo":(50,9550)}
    for z,(x,y) in zonas.items():
        # borrar previo
        for a in list(eas.get_all_level_actors()):
            if a.get_actor_label()=="RelatoCartela_%s"%z: eas.destroy_actor(a)
        fz=gz(x,y)
        act=eas.spawn_actor_from_class(bpclass, unreal.Vector(x,y,fz+160), unreal.Rotator(0,0,0))
        if not act: R["err"].append("spawn_%s"%z); continue
        act.set_actor_label("RelatoCartela_%s"%z)
        mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/Paneles/M_Panel_%s"%z)
        snd=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Audio/Relatos/A_Relato_%s"%z)
        for c in act.get_components_by_class(unreal.ActorComponent):
            cn=c.get_name()
            if cn=="Panel" and mat:
                c.set_material(0, mat)
                c.set_visibility(False); c.set_editor_property("hidden_in_game", True)
            if cn=="Audio" and snd:
                c.set_sound(snd)
            if cn=="Colision":
                if isinstance(c, unreal.BoxComponent): c.set_box_extent(unreal.Vector(300,300,300), True)
                c.set_editor_property("generate_overlap_events", True)
                c.set_collision_profile_name("OverlapAllDynamic")
        R["placed"].append({"z":z,"mat":mat is not None,"snd":snd is not None,"fz":round(fz)})
    # robustez: TODAS las cartelas (19 + relatos) -> Colision overlap ALL (cuerpo Y control disparan)
    for a in eas.get_all_level_actors():
        if "Cartela" in a.get_class().get_name():
            for c in a.get_components_by_class(unreal.PrimitiveComponent):
                if c.get_name()=="Colision":
                    c.set_collision_profile_name("OverlapAllDynamic")
                    c.set_editor_property("generate_overlap_events", True)
                    R["robust"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/narr_entrada.json","w").write(json.dumps(R))
