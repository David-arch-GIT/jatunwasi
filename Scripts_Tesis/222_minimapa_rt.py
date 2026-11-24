# 222_minimapa_rt.py - minimapa TIEMPO REAL: mapa fijo + punto rojo que se mueve con el jugador (solo material, 0 scene capture)
import unreal, json, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    mp="/Game/JWN/UI/M_MinimapaRT"
    tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/T_Minimapa")
    if unreal.EditorAssetLibrary.does_asset_exist(mp):
        unreal.EditorAssetLibrary.delete_asset(mp)
    mat=AT.create_asset("M_MinimapaRT","/Game/JWN/UI",unreal.Material,unreal.MaterialFactoryNew())
    def N(cls,x,y):
        return mel.create_material_expression(mat,cls,x,y)
    # nodos
    tc=N(unreal.MaterialExpressionTextureCoordinate,-900,-200)
    ts=N(unreal.MaterialExpressionTextureSample,-650,-350); ts.set_editor_property("texture",tex)
    mel.connect_material_expressions(tc,"",ts,"UVs")
    op=N(unreal.MaterialExpressionObjectPositionWS,-1300,200)
    mx=N(unreal.MaterialExpressionComponentMask,-1100,120); mx.set_editor_property("r",True); mx.set_editor_property("g",False); mx.set_editor_property("b",False); mx.set_editor_property("a",False)
    my=N(unreal.MaterialExpressionComponentMask,-1100,300); my.set_editor_property("r",False); my.set_editor_property("g",True); my.set_editor_property("b",False); my.set_editor_property("a",False)
    mel.connect_material_expressions(op,"",mx,""); mel.connect_material_expressions(op,"",my,"")
    # uU = opx*5.497e-5 + 0.5359
    mulU=N(unreal.MaterialExpressionMultiply,-900,120); mulU.set_editor_property("const_b",5.497e-05)
    mel.connect_material_expressions(mx,"",mulU,"A")
    addU=N(unreal.MaterialExpressionAdd,-750,120); addU.set_editor_property("const_b",0.5359)
    mel.connect_material_expressions(mulU,"",addU,"A")
    # uV = opy*-6.642e-5 + 0.7857
    mulV=N(unreal.MaterialExpressionMultiply,-900,300); mulV.set_editor_property("const_b",-6.642e-05)
    mel.connect_material_expressions(my,"",mulV,"A")
    addV=N(unreal.MaterialExpressionAdd,-750,300); addV.set_editor_property("const_b",0.7857)
    mel.connect_material_expressions(mulV,"",addV,"A")
    # puv = append(uU,uV)
    app=N(unreal.MaterialExpressionAppendVector,-580,200)
    mel.connect_material_expressions(addU,"",app,"A"); mel.connect_material_expressions(addV,"",app,"B")
    # dist(tc, puv)
    dist=N(unreal.MaterialExpressionDistance,-400,0)
    mel.connect_material_expressions(tc,"",dist,"A"); mel.connect_material_expressions(app,"",dist,"B")
    # mask = clamp((0.024 - dist)*60, 0,1)
    sub=N(unreal.MaterialExpressionSubtract,-250,0); sub.set_editor_property("const_a",0.024)
    mel.connect_material_expressions(dist,"",sub,"B")
    mul2=N(unreal.MaterialExpressionMultiply,-120,0); mul2.set_editor_property("const_b",60.0)
    mel.connect_material_expressions(sub,"",mul2,"A")
    clamp=N(unreal.MaterialExpressionClamp,0,0)
    mel.connect_material_expressions(mul2,"",clamp,"")
    # dotcol rojo
    dot=N(unreal.MaterialExpressionConstant3Vector,-250,180); dot.set_editor_property("constant",unreal.LinearColor(1.0,0.15,0.1,1.0))
    # lerp(map, dot, mask)
    lerp=N(unreal.MaterialExpressionLinearInterpolate,150,-100)
    mel.connect_material_expressions(ts,"RGB",lerp,"A"); mel.connect_material_expressions(dot,"",lerp,"B"); mel.connect_material_expressions(clamp,"",lerp,"Alpha")
    # emissive = lerp*1.3
    emis=N(unreal.MaterialExpressionMultiply,320,-100); emis.set_editor_property("const_b",1.3)
    mel.connect_material_expressions(lerp,"",emis,"A")
    mel.connect_material_property(emis,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("material_RT_ok")
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-600:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/minirt.json","w").write(json.dumps(R))
