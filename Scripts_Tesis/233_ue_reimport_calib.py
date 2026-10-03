import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reimp_calib.json"
at = unreal.AssetToolsHelpers.get_asset_tools()
DEST = "/Game/FotosAntano/Encuadradas"
task = unreal.AssetImportTask()
task.set_editor_property("filename", r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano/Encuadradas/ZZ_CALIB.png")
task.set_editor_property("destination_path", DEST)
task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
at.import_asset_tasks([task])
t = unreal.EditorAssetLibrary.load_asset(DEST+"/ZZ_CALIB")
if t:
    t.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    t.set_editor_property("never_stream", True)
    try: t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    except Exception: pass
    unreal.EditorAssetLibrary.save_asset(DEST+"/ZZ_CALIB", only_if_is_dirty=False)
# recolocar camara de frente a COR_Cuadro_07
eas = unreal.EditorActorSubsystem()
fa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COR_Cuadro_07": fa = a; break
loc = fa.get_actor_location(); rot = fa.get_actor_rotation()
yaw = math.radians(rot.yaw); nx = -math.sin(yaw); ny = math.cos(yaw)
dist = 165.0; zc = loc.z + 43.0
cam = unreal.Vector(loc.x - nx*dist, loc.y - ny*dist, zc)
look = math.degrees(math.atan2(loc.y - cam.y, loc.x - cam.x))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
open(OUT,"w").write(json.dumps({"cam":[round(cam.x),round(cam.y),round(cam.z),round(look,1)]}))
