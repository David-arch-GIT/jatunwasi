import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/loc_verif.json"
res={"apl":[], "catre_comp":None}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl.startswith("APL_") and len(res["apl"])<6:
        loc=a.get_actor_location()
        res["apl"].append({"lbl":lbl,"loc":[round(loc.x),round(loc.y),round(loc.z)]})
    if lbl=="CV2_Catre":
        # bounds reales
        o,e=a.get_actor_bounds(False)
        res["catre_comp"]={"bounds_o":[round(o.x),round(o.y),round(o.z)],"ext":[round(e.x),round(e.y),round(e.z)]}
# camara al origen para ver el catre
cam=unreal.Vector(350, 320, 160)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(0,0,50))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
open(OUT,"w").write(json.dumps(res,indent=1))
