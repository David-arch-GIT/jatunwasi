# Coloca paneles de explicacion (placa holografica) a la entrada de cada escenario.
import unreal, json, math, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"colocados":[], "err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    def floorz(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,1500),unreal.Vector(x,y,-200),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        best=None
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
                if "PCG_" in n: continue
                if best is None or z>best[0]: best=(z,n)
        return best[0] if best else 0
    # 1) importar texturas
    for k in ["plaza","hacienda","convento","templo"]:
        task=unreal.AssetImportTask()
        task.filename="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/panel_%s.png"%k
        task.destination_path="/Game/JWN/UI/Paneles"; task.destination_name="T_Panel_%s"%k
        task.automated=True; task.replace_existing=True; task.save=True
        AT.import_asset_tasks([task])
    # 2) material maestro unlit translucido (una instancia por textura via override simple: un material por panel)
    mel=unreal.MaterialEditingLibrary
    def make_mat(k):
        path="/Game/JWN/UI/Paneles/M_Panel_%s"%k
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            return unreal.EditorAssetLibrary.load_asset(path)
        mat=AT.create_asset("M_Panel_%s"%k,"/Game/JWN/UI/Paneles",unreal.Material,unreal.MaterialFactoryNew())
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/Paneles/T_Panel_%s"%k)
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0)
        ts.set_editor_property("texture",tex)
        mel.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_TRANSLUCENT)
        mat.set_editor_property("two_sided",True)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(path)
        return mat
    # 3) colocaciones: (x,y, normal hacia el visitante)
    plano=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    places={
     "plaza":   (600,-520,  0,-1),
     "hacienda":(-7250,-820, 0.2,1),
     "convento":(5950,4250, -0.1,-1),
     "templo":  (50,9550,   0,-1),
    }
    for k,(x,y,nx,ny) in places.items():
        for a in eas.get_all_level_actors():
            if a.get_actor_label()=="PANEL_%s"%k: eas.destroy_actor(a)
        fz=floorz(x,y)
        mag=math.hypot(nx,ny) or 1.0
        n=unreal.Vector(nx/mag,ny/mag,0)
        rot=unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,-1))
        loc=unreal.Vector(x,y,fz+150)
        act=unreal.EditorLevelLibrary.spawn_actor_from_object(plano, loc, rot)
        act.set_actor_label("PANEL_%s"%k)
        act.set_actor_scale3d(unreal.Vector(2.4,1.8,1.0))
        smc=act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_material(0, make_mat(k))
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        smc.set_editor_property("cast_shadow",False)
        R["colocados"].append({"k":k,"loc":[x,y,fz+150]})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/paneles.json","w").write(json.dumps(R)); print("PANELES", json.dumps({"ok":R.get("ok"),"n":len(R["colocados"])}))
