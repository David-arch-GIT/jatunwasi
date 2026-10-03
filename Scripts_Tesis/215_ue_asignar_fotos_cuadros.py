import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/asignar_fotos.json"
res = {"asignados": [], "sin_foto": [], "err": []}
eas = unreal.EditorActorSubsystem()
# cargar las MI de fotos
mis = []
for p in unreal.EditorAssetLibrary.list_assets("/Game/FotosAntano", recursive=False):
    if "MI_Foto_" in p:
        a = unreal.EditorAssetLibrary.load_asset(p)
        if a: mis.append((p.split("/")[-1].split(".")[0], a))
mis.sort()
# 6 cuadros destino (museo), en orden
DEST_FRAMES = ["MUS_Cuadro_00","MUS_Cuadro_01","MUS_Cuadro_02","MUS_Cuadro_03","MUS_Cuadro_coc0","MUS_Cuadro_coc1"]
frame_actors = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith("MUS_Cuadro") or lab.startswith("COR_Cuadro") or lab.startswith("BALL_Cuadro"):
        frame_actors[lab] = a
# asignar sin repetir
for i, fname in enumerate(DEST_FRAMES):
    if i >= len(mis): break
    a = frame_actors.get(fname)
    if not a:
        res["err"].append("no frame: "+fname); continue
    mi_name, mi = mis[i]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        c.set_material(1, mi)  # slot 1 = canvas
    res["asignados"].append(fname + "  <-  " + mi_name)
# frames sin foto
for lab in frame_actors:
    if lab not in DEST_FRAMES[:len(mis)]:
        res["sin_foto"].append(lab)
res["n_mis"] = len(mis); res["n_frames_total"] = len(frame_actors)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
