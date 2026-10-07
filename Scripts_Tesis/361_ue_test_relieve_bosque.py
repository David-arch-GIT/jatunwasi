# TEST de relieve natural de bosque: cluster de rocas/pena/troncos/tocones/helechos/arbustos
# con posicion, escala y giro ALEATORIOS (no uniforme) en zona de bosque fuera de ruta (-4000,4000).
# Reversible (prefijo REL_TEST_). Solo valida el LOOK; si se aprueba -> PCG instanciado.
import unreal, json, random
random.seed(7)
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_test.json"
res={"placed":0,"missing":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
EAL=unreal.EditorAssetLibrary
eas=unreal.EditorActorSubsystem()
# mapa nombre->path
def pathfor(name):
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True):
        if str(ad.asset_name)==name: return str(ad.package_name)+"."+name
    return None
# paleta: (nombre, cantidad, escala_min, escala_max)
palette=[
 ("SM_ForestRock_01",4,0.6,2.2),("SM_ForestRock_02",4,0.6,2.2),("SM_ForestRock_03",3,0.6,2.0),
 ("SM_Cliff_01",1,0.10,0.22),("SM_Cliff_02",1,0.10,0.22),
 ("SM_FallenLog_01",2,0.7,1.3),("SM_FallenLog_02",1,0.7,1.3),
 ("SM_Stump_Old_01",2,0.7,1.4),("SM_Stump_Cut_01",1,0.7,1.2),
 ("SM_Fern_01",6,0.7,1.6),("SM_Fern_02",5,0.7,1.6),
 ("SM_ForestBush_01",4,0.7,1.5),("SM_ForestBush_02",3,0.7,1.5),
 ("SM_Branches_01",2,0.8,1.4),("SM_Branch_Scatter_01",2,0.8,1.4),
]
CX,CY,GZ=-4000,4000,-5  # centro de bosque fuera de ruta; suelo Ground_Cochabamba top ~ -5
R=2000  # radio del cluster (20 m)
idx=0
for (name,cnt,smin,smax) in palette:
    p=pathfor(name)
    if not p or not EAL.does_asset_exist(p.split(".")[0]):
        res["missing"].append(name); continue
    mesh=EAL.load_asset(p.split(".")[0])
    for i in range(cnt):
        # posicion con ruido gaussiano (cluster natural), evitar centro exacto
        ang=random.uniform(0,6.283); rad=abs(random.gauss(0,0.55))*R
        x=CX+rad*__import__("math").cos(ang); y=CY+rad*__import__("math").sin(ang)
        loc=unreal.Vector(x,y,GZ)
        rot=unreal.Rotator(); rot.yaw=random.uniform(0,360); rot.roll=random.uniform(-4,4); rot.pitch=random.uniform(-4,4)
        act=eas.spawn_actor_from_object(mesh, loc, rot)
        s=random.uniform(smin,smax)
        act.set_actor_scale3d(unreal.Vector(s,s,random.uniform(s*0.85,s*1.15)))
        act.set_actor_label("REL_TEST_%03d_%s"%(idx,name)); idx+=1
        try:
            smc=act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_editor_property("cast_shadow", False)
        except: pass
res["placed"]=idx
# camara para capturar el cluster
cam=unreal.Vector(CX-1500, CY-1500, 450)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(CX,CY,100))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
