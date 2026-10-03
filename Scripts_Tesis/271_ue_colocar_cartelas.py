import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar.json"
res={"puestas":[], "err":[]}
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
plane=EAL.load_asset("/Engine/BasicShapes/Plane")
down=unreal.Vector(0,0,-1)
datos=json.loads(open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/datos_obj.json","r").read())["obj"]
# normal (hacia donde mira la cartela / el visitante)
FACE={
 "varon_valluno":(-1,0),
 "pollera_cochabambina":(0,-1),
 "tarka":(0,-1),
 "habito":(0,-1),
 "altar_convento":(-1,0),
 "urkupina":(0,-1),
 "nino_sikimira":(-1,0),
 "san_sebastian":(1,0),
 "cristo_llora":(1,0),
 "santa_vera_cruz":(-1,0),
 "retablo":(0,-1),
 "altar_mayor":(0,-1),
 "pulpito":(1,0),
 "confesionario":(1,0),
}
# borrar cartelas previas
for a in list(eas.get_all_level_actors()):
    l=a.get_actor_label()
    if l.startswith("Cartela_") or l=="Cartela_SAMPLE": eas.destroy_actor(a)
for cart,(nx,ny) in FACE.items():
    d=datos.get(cart)
    if not d or "err" in d: res["err"].append(cart); continue
    o=d["o"]; e=d["e"]
    ext = e[0] if abs(nx)>0 else e[1]
    off = abs(ext) + 40
    mi=EAL.load_asset("/Game/Cartelas/Tex/MI_Cart_"+cart)
    if not mi: res["err"].append("no MI "+cart); continue
    normal=unreal.Vector(nx,ny,0)
    rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
    pos=unreal.Vector(o[0]+nx*off, o[1]+ny*off, 150.0)
    pl=eas.spawn_actor_from_object(plane, pos, rot)
    pl.set_actor_label("Cartela_"+cart)
    pl.set_actor_scale3d(unreal.Vector(0.95,0.60,1.0))
    smc=pl.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mi); smc.set_cast_shadow(False)
    res["puestas"].append(cart)
res["n"]=len(res["puestas"])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
