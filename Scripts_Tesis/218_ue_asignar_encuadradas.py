import unreal, json, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/encuadradas.json"
res = {"tex": [], "asignados": [], "err": []}
SRCDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano/Encuadradas"
DEST = "/Game/FotosAntano/Encuadradas"
at = unreal.AssetToolsHelpers.get_asset_tools()
mat = unreal.EditorAssetLibrary.load_asset("/Game/FotosAntano/M_FotoAntano")
MEL = unreal.MaterialEditingLibrary
# 1) importar cada PNG encuadrado, crear MI
mis = []
pngs = sorted([f for f in os.listdir(SRCDIR) if f.lower().endswith(".png")])
for f in pngs:
    try:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", os.path.join(SRCDIR, f))
        task.set_editor_property("destination_path", DEST)
        task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
        at.import_asset_tasks([task])
        for p in list(task.get_editor_property("imported_object_paths")):
            base = p.split(".")[0]
            tex = unreal.EditorAssetLibrary.load_asset(base)
            if isinstance(tex, unreal.Texture2D):
                tex.set_editor_property("max_texture_size", 2048)
                unreal.EditorAssetLibrary.save_asset(base, only_if_is_dirty=False)
                nm = "MI_C_" + tex.get_name()[:26]
                ip = "/Game/FotosAntano/Encuadradas/"+nm
                if unreal.EditorAssetLibrary.does_asset_exist(ip): unreal.EditorAssetLibrary.delete_asset(ip)
                mi = at.create_asset(nm, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                MEL.set_material_instance_parent(mi, mat)
                MEL.set_material_instance_texture_parameter_value(mi, "Foto", tex)
                unreal.EditorAssetLibrary.save_asset(ip, only_if_is_dirty=False)
                mis.append(mi)
                res["tex"].append(tex.get_name())
    except Exception as e:
        res["err"].append("imp "+f[:18]+":"+str(e)[:40])
# 2) asignar a los 13 cuadros (slot 1), sin repetir
FRAMES = ["MUS_Cuadro_00","MUS_Cuadro_01","MUS_Cuadro_02","MUS_Cuadro_03","MUS_Cuadro_coc0","MUS_Cuadro_coc1","MUS_Cuadro_dorm0","BALL_Cuadro_0","BALL_Cuadro_1","COR_Cuadro_00","COR_Cuadro_01","COR_Cuadro_03","COR_Cuadro_07"]
eas = unreal.EditorActorSubsystem()
fa = {}
for a in eas.get_all_level_actors():
    if a.get_actor_label() in FRAMES: fa[a.get_actor_label()] = a
for i, fn in enumerate(FRAMES):
    if i >= len(mis): break
    a = fa.get(fn)
    if not a: res["err"].append("no frame "+fn); continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        c.set_material(1, mis[i])
    res["asignados"].append(fn + " <- " + mis[i].get_name())
res["n_tex"] = len(mis); res["n_frames"] = len(fa)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
