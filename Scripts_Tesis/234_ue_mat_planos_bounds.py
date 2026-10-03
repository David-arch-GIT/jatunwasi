import unreal, json, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mat_planos.json"
res = {"mi": [], "bounds": [], "err": []}
at = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
BASE = "/Game/FotosAntano"
DEST = BASE + "/Planos"
SRCDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano/Planos"

# 1) material unlit M_FotoPlane
mp = BASE + "/M_FotoPlane"
if EAL.does_asset_exist(mp): EAL.delete_asset(mp)
mat = at.create_asset("M_FotoPlane", BASE, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
tp = MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -400, 0)
tp.set_editor_property("parameter_name", "Foto")
mul = MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -160, 0)
mul.set_editor_property("const_b", 1.15)
MEL.connect_material_expressions(tp, "RGB", mul, "A")
MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.recompile_material(mat)
EAL.save_asset(mp, only_if_is_dirty=False)

# 2) importar 14 planos + MI_P_
for f in sorted(os.listdir(SRCDIR)):
    if not f.lower().endswith(".png"): continue
    try:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", os.path.join(SRCDIR, f))
        task.set_editor_property("destination_path", DEST)
        task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
        at.import_asset_tasks([task])
        for p in list(task.get_editor_property("imported_object_paths")):
            base = p.split(".")[0]
            tex = EAL.load_asset(base)
            if isinstance(tex, unreal.Texture2D):
                tex.set_editor_property("max_texture_size", 2048)
                tex.set_editor_property("never_stream", True)
                try: tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_BC7)
                except Exception: pass
                try: tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_SHARPEN3)
                except Exception: pass
                EAL.save_asset(base, only_if_is_dirty=False)
                nm = "MI_P_" + tex.get_name()[:26]
                ip = DEST + "/" + nm
                if EAL.does_asset_exist(ip): EAL.delete_asset(ip)
                mi = at.create_asset(nm, DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                MEL.set_material_instance_parent(mi, mat)
                MEL.set_material_instance_texture_parameter_value(mi, "Foto", tex)
                EAL.save_asset(ip, only_if_is_dirty=False)
                res["mi"].append(nm)
    except Exception as e:
        res["err"].append(f[:16]+":"+str(e)[:40])

# 3) bounds de los 13 cuadros
FRAMES = ["MUS_Cuadro_00","MUS_Cuadro_01","MUS_Cuadro_02","MUS_Cuadro_03","MUS_Cuadro_coc0","MUS_Cuadro_coc1","MUS_Cuadro_dorm0","BALL_Cuadro_0","BALL_Cuadro_1","COR_Cuadro_00","COR_Cuadro_01","COR_Cuadro_03","COR_Cuadro_07"]
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_actor_label() in FRAMES:
        o, e = a.get_actor_bounds(False)
        rot = a.get_actor_rotation()
        res["bounds"].append({"lbl": a.get_actor_label(),
            "origin": [round(o.x,1), round(o.y,1), round(o.z,1)],
            "ext": [round(e.x,1), round(e.y,1), round(e.z,1)],
            "yaw": round(rot.yaw,2)})
res["n_mi"] = len(res["mi"]); res["n_bounds"] = len(res["bounds"])
open(OUT, "w").write(json.dumps(res, indent=1))
