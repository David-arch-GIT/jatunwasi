import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fixbox.json"
res={"ok":[], "err":[]}
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
OBJ={
 "varon_valluno":"HF_ManiquiM_G","pollera_cochabambina":"HF_ManiquiF_G",
 "charango":"HF_Charango_G","zampona":"HF_Zampona","quena":"HF_Quena_G",
 "acordeon":"HF_Bombo","tarka":"HF_Tarka","catre":None,
 "habito":"VIT_Habito_Mesh","altar_convento":"CONV_Altar",
 "urkupina":"Santo_Virgen_Urkupina","nino_sikimira":"Santo_Nino_Sikimira",
 "san_sebastian":"Santo_San_Sebastian","cristo_llora":"Santo_Cristo_Llorando",
 "santa_vera_cruz":"Santo_Santa_Vera_Cruz","retablo":"Retablo_Barroco_Mayor",
 "altar_mayor":"Altar_Mayor_Exento","pulpito":"Pulpito","confesionario":"Confesionario_Nuevo_L",
}
byl={}
for a in eas.get_all_level_actors(): byl[a.get_actor_label()]=a
QueryOnly=unreal.CollisionEnabled.QUERY_ONLY
for cart,objlbl in OBJ.items():
  try:
    act=byl.get("Cartela_"+cart)
    if not act: res["err"].append("no act "+cart); continue
    box=None; audio=None; panel=None
    for c in act.get_components_by_class(unreal.BoxComponent): box=c
    for c in act.get_components_by_class(unreal.AudioComponent): audio=c
    for c in act.get_components_by_class(unreal.StaticMeshComponent): panel=c
    # ubicacion colision = objeto (o panel si no hay objeto)
    obj=byl.get(objlbl) if objlbl else None
    if obj:
        o,e=obj.get_actor_bounds(False); cloc=unreal.Vector(o.x,o.y,o.z)
    elif panel:
        pw=panel.get_world_location(); cloc=unreal.Vector(pw.x,pw.y,pw.z)
    else:
        cloc=act.get_actor_location()
    if box:
        box.set_world_location(cloc, False, False)
        box.set_box_extent(unreal.Vector(75,75,100), True)
        box.set_collision_profile_name("BlockAll")
        box.set_collision_enabled(QueryOnly)
        box.set_editor_property("hidden_in_game", True)
    if audio:
        snd=EAL.load_asset("/Game/Cartelas/Audio/"+cart)
        if snd: audio.set_sound(snd)
        audio.set_editor_property("auto_activate", False)
    res["ok"].append(cart)
  except Exception as e:
    res["err"].append(cart+":"+str(e)[:70])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ok"])
open(OUT,"w").write(json.dumps(res,indent=1))
