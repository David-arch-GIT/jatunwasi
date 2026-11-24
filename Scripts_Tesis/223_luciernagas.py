# 223_luciernagas.py - luciernagas que titilan (HISM esferas + material emisivo pulsante por Time, barato Quest)
import unreal, json, math, random, traceback
R={"steps":[],"n":0,"err":[]}
random.seed(21)
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # material luciernaga (unlit emisivo que titila; fase por PerInstanceRandom)
    mp="/Game/JWN/FX/M_Firefly"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_Firefly","/Game/JWN/FX",unreal.Material,unreal.MaterialFactoryNew())
        tm=mel.create_material_expression(mat,unreal.MaterialExpressionTime,-800,0)
        spd=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-650,0); spd.set_editor_property("const_b",2.2)
        mel.connect_material_expressions(tm,"",spd,"A")
        pir=mel.create_material_expression(mat,unreal.MaterialExpressionPerInstanceRandom,-800,180)
        pph=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-650,180); pph.set_editor_property("const_b",6.283)
        mel.connect_material_expressions(pir,"",pph,"A")
        add=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,-500,90)
        mel.connect_material_expressions(spd,"",add,"A"); mel.connect_material_expressions(pph,"",add,"B")
        sinx=mel.create_material_expression(mat,unreal.MaterialExpressionSine,-350,90)
        mel.connect_material_expressions(add,"",sinx,"")
        # 0.1 + 0.9*clamp(sin)  -> parpadeo
        h=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,90); h.set_editor_property("const_b",0.9)
        mel.connect_material_expressions(sinx,"",h,"A")
        base=mel.create_material_expression(mat,unreal.MaterialExpressionAdd,-60,90); base.set_editor_property("const_b",0.15)
        mel.connect_material_expressions(h,"",base,"A")
        col=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-200,-80); col.set_editor_property("constant",unreal.LinearColor(1.0,0.85,0.35,1.0))
        emi=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,120,0)
        mel.connect_material_expressions(col,"",emi,"A"); mel.connect_material_expressions(base,"",emi,"B")
        boost=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,280,0); boost.set_editor_property("const_b",4.0)
        mel.connect_material_expressions(emi,"",boost,"A")
        mel.connect_material_property(boost,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("mat")
    fmat=unreal.EditorAssetLibrary.load_asset(mp)
    sph=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    # actor HISM para luciernagas
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="FX_Luciernagas": eas.destroy_actor(a)
    act=eas.spawn_actor_from_class(unreal.Actor, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    act.set_actor_label("FX_Luciernagas")
    hism=act.add_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent, False, unreal.Transform(), False)
    hism.set_static_mesh(sph); hism.set_material(0, fmat)
    hism.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    hism.set_editor_property("cast_shadow", False)
    hism.set_editor_property("instance_start_cull_distance", 4000)
    hism.set_editor_property("instance_end_cull_distance", 6000)
    # zonas con jardin/arboles donde flotan
    centers=[(0,-1000,900),(-750,-400,500),(3400,1750,500),(600,-520,400),(5950,4250,600),(50,9550,600),(-4135,668,500),(-7250,-820,500)]
    for cx,cy,rad in centers:
        for i in range(22):
            ang=random.uniform(0,6.283); r=random.uniform(80,rad)
            x=cx+math.cos(ang)*r; y=cy+math.sin(ang)*r; z=random.uniform(50,210)
            tr=unreal.Transform(unreal.Vector(x,y,z), unreal.Rotator(0,0,0), unreal.Vector(0.035,0.035,0.035))
            hism.add_instance(tr); R["n"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luciernagas.json","w").write(json.dumps(R))
