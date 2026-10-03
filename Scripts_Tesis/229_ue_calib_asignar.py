import unreal, json, math, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/calib_asignar.json"
res = {}
at = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
DEST = "/Game/FotosAntano/Encuadradas"
# 1) importar ZZ_CALIB
task = unreal.AssetImportTask()
task.set_editor_property("filename", r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano/Encuadradas/ZZ_CALIB.png")
task.set_editor_property("destination_path", DEST)
task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
at.import_asset_tasks([task])
tex = unreal.EditorAssetLibrary.load_asset(DEST+"/ZZ_CALIB")
res["tex"] = tex.get_name() if tex else None
# 2) MI_CALIB
mat = unreal.EditorAssetLibrary.load_asset("/Game/FotosAntano/M_FotoAntano")
ip = DEST+"/MI_CALIB"
if unreal.EditorAssetLibrary.does_asset_exist(ip): unreal.EditorAssetLibrary.delete_asset(ip)
mi = at.create_asset("MI_CALIB", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, mat)
MEL.set_material_instance_texture_parameter_value(mi, "Foto", tex)
unreal.EditorAssetLibrary.save_asset(ip, only_if_is_dirty=False)
# 3) asignar a COR_Cuadro_07 slot 1 (guardar material previo)
eas = unreal.EditorActorSubsystem()
fa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COR_Cuadro_07": fa = a; break
if fa:
    for c in fa.get_components_by_class(unreal.StaticMeshComponent):
        prev = c.get_material(1)
        res["prev_mat"] = prev.get_name() if prev else None
        c.set_material(1, mi)
    loc = fa.get_actor_location(); rot = fa.get_actor_rotation()
    yaw = math.radians(rot.yaw); nx = -math.sin(yaw); ny = math.cos(yaw)
    dist = 95.0
    cam = unreal.Vector(loc.x + nx*dist, loc.y + ny*dist, loc.z + 10.0)
    look = math.degrees(math.atan2(loc.y - cam.y, loc.x - cam.x))
    eas.set_selected_level_actors([])
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
    res["cam"] = [round(cam.x), round(cam.y), round(cam.z), round(look,1)]
open(OUT,"w").write(json.dumps(res, indent=1))
