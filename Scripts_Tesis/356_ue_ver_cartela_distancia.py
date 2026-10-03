# Encuadra una cartela del templo desde ~4m (distancia realista frenado por bancas) para ver legibilidad.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ver_cartela.json"
res={}
eas=unreal.EditorActorSubsystem()
eas.set_selected_level_actors([])
# buscar una cartela del templo
CANDS=["san_sebastian","cristo_llora","urkupina","vera_cruz","sikimira","retablo","altar_mayor","pulpito"]
target=None
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label().lower()
    if "cartela" in lbl and any(k in lbl for k in CANDS):
        target=a; res["cartela"]=a.get_actor_label(); break
if target is None:
    for a in eas.get_all_level_actors():
        if "BP_Cartela" in a.get_class().get_name():
            target=a; res["cartela"]=a.get_actor_label()+" (cualquiera)"; break
if target:
    loc=target.get_actor_location()
    res["loc"]=[round(loc.x),round(loc.y),round(loc.z)]
    # panel normal: la cartela mira hacia su -X o +X? probamos camara a 400cm en varias; usamos hacia el jugador tipico
    # ponemos camara 400cm "adelante" (asumimos frente en -Y o segun); probamos 4 lados y elegimos el que mira al panel
    fwd=target.get_actor_forward_vector()
    cam=unreal.Vector(loc.x - fwd.x*420, loc.y - fwd.y*420, loc.z + 20)
    look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    ues.set_level_viewport_camera_info(cam, look)
    try:
        les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.editor_set_game_view(True)
    except Exception: pass
    res["cam"]=[round(cam.x),round(cam.y),round(cam.z)]
unreal.EditorLevelLibrary.editor_invalidate_viewports()
open(OUT,"w").write(json.dumps(res,indent=1))
