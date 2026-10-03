import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/forma_cuadro.json"
res = {"frames": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not (lab.endswith("Cuadro_00") or lab=="MUS_Cuadro_00" or lab=="MUS_Cuadro_01" or lab=="BALL_Cuadro_0"):
        continue
    loc = a.get_actor_location(); rot = a.get_actor_rotation(); sc = a.get_actor_scale3d()
    org, ext = a.get_actor_bounds(False)
    res["frames"].append({
        "label": lab,
        "yaw": round(rot.yaw,1),
        "scale": [round(sc.x,2),round(sc.y,2),round(sc.z,2)],
        "ext_mundo": [round(ext.x*2),round(ext.y*2),round(ext.z*2)]  # ancho total en X,Y,Z (mundo)
    })
# tambien las dimensiones locales del mesh FN_Cuadro
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for a in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True):
    if str(a.asset_name)!="FN_Cuadro": continue
    m=unreal.EditorAssetLibrary.load_asset(str(a.package_name))
    b=m.get_bounds().box_extent
    res["mesh_FN_Cuadro_ext"]=[round(b.x*2),round(b.y*2),round(b.z*2)]
    break
open(OUT,"w").write(json.dumps(res, indent=1))
