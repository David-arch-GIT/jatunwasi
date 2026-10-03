# Encuadra un SM_JW_WallLantern y compara materiales de vidrio (LampEmissive vs FarolCalido).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspect_farol.json"
res={}
eas=unreal.EditorActorSubsystem()
wall=None; wall_actor=None; plaza=None
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        sm=c.get_editor_property("static_mesh")
        if not sm: continue
        nm=sm.get_name()
        if nm=="SM_JW_WallLantern" and wall is None:
            wall=c; wall_actor=a
        if nm=="SM_PLZT_ColonialLamp" and plaza is None:
            plaza=c
def minfo(c, slot):
    if c is None: return {"err":"no comp"}
    ov=c.get_editor_property("override_materials")
    m=ov[slot] if len(ov)>slot else None
    if not m: return {"mat":"None"}
    d={"mat":m.get_name(),"path":m.get_path_name(),"clase":m.get_class().get_name()}
    try:
        base=m.get_base_material()
        d["shading"]=str(base.get_editor_property("shading_model"))
        d["blend"]=str(base.get_editor_property("blend_mode"))
        d["twosided"]=bool(base.get_editor_property("two_sided"))
    except Exception as e:
        d["dbg"]=str(e)[:60]
    return d
res["wall_glass"]=minfo(wall,1)
res["wall_iron"]=minfo(wall,0)
res["plaza_glass"]=minfo(plaza,1)
res["plaza_iron"]=minfo(plaza,0)

# Encuadre camara al primer wall lantern (ISM instancia 0)
try:
    if wall:
        try:
            t=wall.get_instance_transform(0, True)
            loc=t.translation
        except Exception:
            loc=wall_actor.get_actor_location()
        cam=unreal.Vector(loc.x+150, loc.y+150, loc.z+30)
        look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
        ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        ues.set_level_viewport_camera_info(cam, look)
        res["cam"]={"loc":[loc.x,loc.y,loc.z]}
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception as e:
    res["cam_err"]=str(e)[:80]
open(OUT,"w").write(json.dumps(res,indent=1))
