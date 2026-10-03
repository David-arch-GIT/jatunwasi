import unreal, json, os
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/import_cartelas.json"
res={"tex":[], "audio":[], "mi":[], "err":[]}
at=unreal.AssetToolsHelpers.get_asset_tools()
EAL=unreal.EditorAssetLibrary
MEL=unreal.MaterialEditingLibrary
TEXSRC=r"C:/UnrealProjects/JatunWasiNawpakay/Content/Cartelas/Tex"
AUDSRC=r"C:/UnrealProjects/JatunWasiNawpakay/Content/Cartelas/Audio"
TEXDEST="/Game/Cartelas/Tex"
AUDDEST="/Game/Cartelas/Audio"
BASE="/Game/Cartelas"

# 1) material holografico M_Cartela (unlit, translucido)
mp=BASE+"/M_Cartela"
if EAL.does_asset_exist(mp): EAL.delete_asset(mp)
mat=at.create_asset("M_Cartela", BASE, unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("two_sided", True)
tp=MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -450, 0)
tp.set_editor_property("parameter_name", "Cartela")
mul=MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, -60)
mul.set_editor_property("const_b", 1.25)
MEL.connect_material_expressions(tp, "RGB", mul, "A")
MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.connect_material_expressions(tp, "A", MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -180, 120), "A")
# opacidad directo del alpha
MEL.connect_material_property(tp, "A", unreal.MaterialProperty.MP_OPACITY)
MEL.recompile_material(mat)
EAL.save_asset(mp, only_if_is_dirty=False)

items=json.loads(open(r"C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis/cartelas.json","r",encoding="utf-8").read())
def import_one(fn, src, dest, maxsize=None):
    task=unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(src, fn))
    task.set_editor_property("destination_path", dest)
    task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
    at.import_asset_tasks([task])
    return list(task.get_editor_property("imported_object_paths"))

for it in items:
    f=it["file"]
    try:
        # textura
        for p in import_one(f+".png", TEXSRC, TEXDEST):
            base=p.split(".")[0]
            tex=EAL.load_asset(base)
            if isinstance(tex, unreal.Texture2D):
                tex.set_editor_property("srgb", True)
                tex.set_editor_property("never_stream", True)
                try: tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_BC7)
                except Exception: pass
                EAL.save_asset(base, only_if_is_dirty=False)
                res["tex"].append(tex.get_name())
                # MI
                nm="MI_Cart_"+f
                ip=TEXDEST+"/"+nm
                if EAL.does_asset_exist(ip): EAL.delete_asset(ip)
                mi=at.create_asset(nm, TEXDEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
                MEL.set_material_instance_parent(mi, mat)
                MEL.set_material_instance_texture_parameter_value(mi, "Cartela", tex)
                EAL.save_asset(ip, only_if_is_dirty=False)
                res["mi"].append(nm)
        # audio
        for p in import_one(f+".wav", AUDSRC, AUDDEST):
            base=p.split(".")[0]
            snd=EAL.load_asset(base)
            if snd: res["audio"].append(snd.get_name())
    except Exception as e:
        res["err"].append(f+":"+str(e)[:50])
res["n_tex"]=len(res["tex"]); res["n_audio"]=len(res["audio"]); res["n_mi"]=len(res["mi"])
open(OUT,"w").write(json.dumps(res, indent=1))
