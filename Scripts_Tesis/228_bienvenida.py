# 228_bienvenida.py - cartela de bienvenida en el PlayerStart (contexto + recorrido + voz guia)
import unreal, json, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # importar textura panel + voz
    tt=unreal.AssetImportTask(); tt.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/welcome/T_Panel_bienvenida.png")
    tt.set_editor_property("destination_path","/Game/JWN/UI/Paneles"); tt.set_editor_property("destination_name","T_Panel_bienvenida")
    tt.set_editor_property("automated",True); tt.set_editor_property("replace_existing",True); tt.set_editor_property("save",True)
    AT.import_asset_tasks([tt])
    ta=unreal.AssetImportTask(); ta.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Content/JWN/Audio/Relatos/relato_bienvenida.wav")
    ta.set_editor_property("destination_path","/Game/JWN/Audio/Relatos"); ta.set_editor_property("destination_name","A_Relato_bienvenida")
    ta.set_editor_property("automated",True); ta.set_editor_property("replace_existing",True); ta.set_editor_property("save",True)
    AT.import_asset_tasks([ta])
    R["steps"].append("imported")
    # material panel (unlit translucido, emissive=rgb, opacity=a)
    mp="/Game/JWN/UI/Paneles/M_Panel_bienvenida"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_Panel_bienvenida","/Game/JWN/UI/Paneles",unreal.Material,unreal.MaterialFactoryNew())
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/Paneles/T_Panel_bienvenida")
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property("texture",tex)
        mel.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_TRANSLUCENT); mat.set_editor_property("two_sided",True)
        mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("mat")
    # ubicacion del PlayerStart
    ps=None
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=="PlayerStart": ps=a; break
    loc=ps.get_actor_location() if ps else unreal.Vector(0,-1000,120)
    R["playerstart"]=[round(loc.x),round(loc.y),round(loc.z)]
    # colocar BP_Cartela de bienvenida
    bpclass=unreal.EditorAssetLibrary.load_blueprint_class("/Game/Cartelas/BP_Cartela")
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="RelatoCartela_bienvenida": eas.destroy_actor(a)
    act=eas.spawn_actor_from_class(bpclass, unreal.Vector(loc.x,loc.y,loc.z+40), unreal.Rotator(0,0,0))
    act.set_actor_label("RelatoCartela_bienvenida")
    mat=unreal.EditorAssetLibrary.load_asset(mp)
    snd=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Audio/Relatos/A_Relato_bienvenida")
    for c in act.get_components_by_class(unreal.ActorComponent):
        cn=c.get_name()
        if cn=="Panel" and mat:
            c.set_material(0, mat); c.set_visibility(False); c.set_editor_property("hidden_in_game", True)
        if cn=="Audio" and snd: c.set_sound(snd)
        if cn=="Colision":
            if isinstance(c, unreal.BoxComponent): c.set_box_extent(unreal.Vector(350,350,350), True)
            c.set_editor_property("generate_overlap_events", True); c.set_collision_profile_name("OverlapAllDynamic")
    R["steps"].append("cartela_colocada"); R["ok"]=True
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bienvenida.json","w").write(json.dumps(R))
