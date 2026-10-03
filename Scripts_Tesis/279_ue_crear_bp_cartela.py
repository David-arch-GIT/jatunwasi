import unreal, json, traceback
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bpcartela.json"
res={"steps":[], "err":None}
try:
    at=unreal.AssetToolsHelpers.get_asset_tools()
    EAL=unreal.EditorAssetLibrary
    BP="/Game/Cartelas/BP_Cartela"
    if EAL.does_asset_exist(BP): EAL.delete_asset(BP)
    # crear blueprint parent Actor
    f=unreal.BlueprintFactory()
    f.set_editor_property("parent_class", unreal.Actor)
    bp=at.create_asset("BP_Cartela","/Game/Cartelas",unreal.Blueprint,f)
    res["steps"].append("bp creado")
    # subobject subsystem para agregar componentes
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    res["steps"].append("handles="+str(len(handles)))
    root=handles[0]
    def add_comp(cls, name, parent):
        params=unreal.AddNewSubobjectParams()
        params.parent_handle=parent
        params.new_class=cls
        params.blueprint_context=bp
        h,fail=sds.add_new_subobject(params)
        if str(fail): res["steps"].append("fail "+name+":"+str(fail))
        sds.rename_subobject(h, name)
        return h
    hbox=add_comp(unreal.BoxComponent,"Colision",root)
    hpanel=add_comp(unreal.StaticMeshComponent,"Panel",root)
    haudio=add_comp(unreal.AudioComponent,"Audio",root)
    res["steps"].append("componentes agregados")
    # variable Abierto (bool)
    unreal.BlueprintEditorLibrary.add_member_variable(bp,"Abierto",unreal.BlueprintEditorLibrary.get_basic_type_by_name("bool"))
    res["steps"].append("var Abierto")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_asset(BP, only_if_is_dirty=False)
    res["ok"]=True
except Exception as e:
    res["err"]=str(e)+" | "+traceback.format_exc()[:400]
open(OUT,"w").write(json.dumps(res,indent=1))
