# 189_ue_paneles_postes_y_limpieza.py
# 1) Oculta el subtitulo TextRender redundante de los RELATO_*.
# 2) Baja los PANEL_* y les agrega 2 postes (letrero con patas) para que no floten.
import unreal, json, math, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"postes":[], "err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    def floorz(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,1500),unreal.Vector(x,y,-200),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        best=None
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
                if "PCG_" in n or "PANEL_" in n or "RELATO_" in n: continue
                if best is None or z>best[0]: best=(z,n)
        return best[0] if best else 0
    # material poste (unlit bronce oscuro)
    mp="/Game/JWN/UI/Paneles/M_JW_Poste"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_JW_Poste","/Game/JWN/UI/Paneles",unreal.Material,unreal.MaterialFactoryNew())
        c=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
        c.set_editor_property("constant",unreal.LinearColor(0.08,0.06,0.04,1.0))
        mel.connect_material_property(c,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(mp)
    postmat=unreal.EditorAssetLibrary.load_asset(mp)
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    # normales de cada panel (de script 187)
    norms={"plaza":(0,-1),"hacienda":(0.2,1),"convento":(-0.1,-1),"templo":(0,-1)}
    # 1) ocultar subtitulos
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("RELATO_"):
            tr=a.get_component_by_class(unreal.TextRenderComponent)
            if tr:
                tr.set_visibility(False)
                tr.set_editor_property("hidden_in_game", True)
    # 2) paneles: bajar + postes
    for a in list(eas.get_all_level_actors()):
        lbl=a.get_actor_label()
        if lbl.startswith("PANEL_"):
            z=lbl.split("_",1)[1]
            loc=a.get_actor_location()
            fz=floorz(loc.x, loc.y)
            # nueva altura: centro a fz+130 (borde inferior ~ fz+40)
            new_center=fz+130.0
            a.set_actor_location(unreal.Vector(loc.x,loc.y,new_center), False, True)
            half_h=90.0  # mitad alto panel (scale1.8 -> 180cm)
            bottom=new_center-half_h
            # vector derecha del panel (perp a normal)
            nx,ny=norms.get(z,(0,-1)); mag=math.hypot(nx,ny) or 1.0
            nx,ny=nx/mag,ny/mag
            rx,ry=-ny,nx  # derecha
            half_w=100.0
            post_h=bottom-fz
            if post_h<20: post_h=20.0
            # limpiar postes previos
            for b in eas.get_all_level_actors():
                if b.get_actor_label().startswith("POSTE_%s_"%z): eas.destroy_actor(b)
            for i,s in enumerate([-1,1]):
                px=loc.x+rx*half_w*s; py=loc.y+ry*half_w*s
                pz=fz+post_h/2.0
                post=unreal.EditorLevelLibrary.spawn_actor_from_object(cyl, unreal.Vector(px,py,pz), unreal.Rotator(0,0,0))
                post.set_actor_label("POSTE_%s_%d"%(z,i))
                post.set_actor_scale3d(unreal.Vector(0.06,0.06,post_h/100.0))
                smc=post.get_component_by_class(unreal.StaticMeshComponent)
                smc.set_material(0, postmat)
                smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                smc.set_editor_property("cast_shadow",False)
            R["postes"].append({"z":z,"fz":fz,"center":new_center,"post_h":round(post_h)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open(out+"/postes.json","w").write(json.dumps(R))
