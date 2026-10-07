# Capa de DENSIDAD (carpeteo) para el test de relieve: sotobosque pequeno y denso
# que cubre el piso entre las rocas grandes, con ruido. Prefijo REL_TEST_ (reversible).
import unreal, json, random, math
random.seed(21)
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_dens.json"
res={"placed":0,"missing":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
EAL=unreal.EditorAssetLibrary
eas=unreal.EditorActorSubsystem()
def pathfor(name):
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True):
        if str(ad.asset_name)==name: return str(ad.package_name)
    return None
# carpeteo: pequeno, denso, baja altura
palette=[
 ("SM_Mossy_Grass_01",14,0.8,1.8),("SM_Mossy_Grass_02",12,0.8,1.8),
 ("SM_Fern_01",10,0.5,1.1),("SM_Fern_02",9,0.5,1.1),
 ("SM_ForestBush_01",6,0.5,1.0),("SM_ForestBush_02",5,0.5,1.0),
 ("SM_ForestRock_01",5,0.15,0.5),("SM_ForestRock_02",5,0.15,0.5),("SM_ForestRock_03",4,0.15,0.45),
 ("SM_Branch_Scatter_01",5,0.7,1.3),("SM_Branch_Scatter_02",4,0.7,1.3),
]
CX,CY,GZ=-4000,4000,-5
R=2200
idx=1000
for (name,cnt,smin,smax) in palette:
    pkg=pathfor(name)
    if not pkg or not EAL.does_asset_exist(pkg):
        res["missing"].append(name); continue
    mesh=EAL.load_asset(pkg)
    for i in range(cnt):
        ang=random.uniform(0,6.283); rad=abs(random.gauss(0,0.62))*R
        x=CX+rad*math.cos(ang); y=CY+rad*math.sin(ang)
        rot=unreal.Rotator(); rot.yaw=random.uniform(0,360); rot.roll=random.uniform(-3,3); rot.pitch=random.uniform(-3,3)
        act=eas.spawn_actor_from_object(mesh, unreal.Vector(x,y,GZ), rot)
        s=random.uniform(smin,smax)
        act.set_actor_scale3d(unreal.Vector(s,s,random.uniform(s*0.85,s*1.15)))
        act.set_actor_label("REL_TEST_%04d_%s"%(idx,name)); idx+=1
        try:
            smc=act.get_component_by_class(unreal.StaticMeshComponent)
            smc.set_editor_property("cast_shadow", False)
        except: pass
res["placed"]=idx-1000
cam=unreal.Vector(CX-700, CY-1000, 170)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(CX+200,CY+300,40))
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
