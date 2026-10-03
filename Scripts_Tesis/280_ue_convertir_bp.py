import unreal, json, traceback
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/convertir.json"
res={"ok":[], "err":[]}
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
ELL=unreal.EditorLevelLibrary
plane_mesh=EAL.load_asset("/Engine/BasicShapes/Plane")
bp=EAL.load_asset("/Game/Cartelas/BP_Cartela")
bpclass=bp.generated_class()
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
NoColl=unreal.CollisionEnabled.NO_COLLISION
QueryOnly=unreal.CollisionEnabled.QUERY_ONLY
for cart,objlbl in OBJ.items():
  try:
    plane=byl.get("Cartela_"+cart)
    if not plane: res["err"].append("no plane "+cart); continue
    ploc=plane.get_actor_location(); prot=plane.get_actor_rotation(); pscl=plane.get_actor_scale3d()
    # ubicacion de la colision (objeto)
    obj=byl.get(objlbl) if objlbl else None
    if obj:
        o,e=obj.get_actor_bounds(False); cloc=unreal.Vector(o.x,o.y,o.z)
    else:
        cloc=unreal.Vector(ploc.x,ploc.y,ploc.z)
    # borrar plano viejo
    eas.destroy_actor(plane)
    # spawn BP_Cartela en el objeto
    act=ELL.spawn_actor_from_class(bpclass, cloc, unreal.Rotator(0,0,0))
    act.set_actor_label("Cartela_"+cart)
    mi=EAL.load_asset("/Game/Cartelas/Tex/MI_Cart_"+cart)
    snd=EAL.load_asset("/Game/Cartelas/Audio/"+cart)
    panel=None; box=None; audio=None
    for c in act.get_components_by_class(unreal.StaticMeshComponent): panel=c
    for c in act.get_components_by_class(unreal.BoxComponent): box=c
    for c in act.get_components_by_class(unreal.AudioComponent): audio=c
    # PANEL: mesh plane, material, transform, oculto, sin colision
    if panel:
        panel.set_static_mesh(plane_mesh)
        if mi: panel.set_material(0, mi)
        panel.set_world_location_and_rotation(ploc, prot, False, False)
        panel.set_world_scale3d(pscl)
        panel.set_editor_property("hidden_in_game", True)
        panel.set_collision_enabled(NoColl)
        panel.set_editor_property("cast_shadow", False)
    # COLISION: caja sobre el objeto, query-only, bloquea trazas
    if box:
        box.set_world_location(cloc)
        box.set_box_extent(unreal.Vector(70,70,95), True)
        box.set_collision_enabled(QueryOnly)
        box.set_collision_response_to_all_channels(unreal.CollisionResponse.ECR_BLOCK)
        box.set_editor_property("hidden_in_game", True)
    # AUDIO
    if audio:
        if snd: audio.set_sound(snd)
        audio.set_editor_property("auto_activate", False)
    res["ok"].append(cart)
  except Exception as e:
    res["err"].append(cart+":"+str(e)[:70])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["ok"])
open(OUT,"w").write(json.dumps(res,indent=1))
