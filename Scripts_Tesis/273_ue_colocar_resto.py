import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/resto.json"
res={"puestas":[], "err":[], "catre_loc":None}
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
plane=EAL.load_asset("/Engine/BasicShapes/Plane")
down=unreal.Vector(0,0,-1)
byl={}
for a in eas.get_all_level_actors(): byl[a.get_actor_label()]=a
# catre: usar world loc del mesh component
catre=byl.get("CV2_Catre")
cloc=None
if catre:
    for c in catre.get_components_by_class(unreal.StaticMeshComponent):
        w=c.get_world_location(); cloc=[round(w.x,1),round(w.y,1),round(w.z,1)]; break
res["catre_loc"]=cloc
# lista: cartela -> (label objeto, normal)
PLAN=[
 ("charango","HF_Charango_G",(0,-1)),
 ("zampona","HF_Zampona",(0,-1)),
 ("quena","HF_Quena_G",(0,-1)),
 ("acordeon","HF_Bombo",(0,-1)),
]
def place(cart, loc, nx, ny, zc):
    mi=EAL.load_asset("/Game/Cartelas/Tex/MI_Cart_"+cart)
    if not mi: res["err"].append("no MI "+cart); return
    normal=unreal.Vector(nx,ny,0)
    rot=unreal.MathLibrary.make_rot_from_zy(normal, down)
    pos=unreal.Vector(loc[0]+nx*55, loc[1]+ny*55, zc)
    pl=eas.spawn_actor_from_object(plane, pos, rot)
    pl.set_actor_label("Cartela_"+cart)
    pl.set_actor_scale3d(unreal.Vector(0.80,0.50,1.0))
    smc=pl.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mi); smc.set_cast_shadow(False)
    res["puestas"].append(cart)
for cart,lbl,(nx,ny) in PLAN:
    a=byl.get(lbl)
    if not a: res["err"].append("no obj "+lbl); continue
    w=a.get_actor_location()
    place(cart,[w.x,w.y,w.z],nx,ny,150.0)
# catre
if cloc:
    place("catre", cloc, 0,-1, cloc[2]+90)
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
res["n"]=len(res["puestas"])
open(OUT,"w").write(json.dumps(res,indent=1))
