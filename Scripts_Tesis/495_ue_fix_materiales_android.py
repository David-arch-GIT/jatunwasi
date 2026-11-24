# 495_ue_fix_materiales_android.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG REAL (previo, en logs desde 2026-11-22): 3 materiales NO compilaban para Android
#   (SF_VULKAN_ES31_ANDROID) y en el visor salian con el material por defecto (gris de cuadricula):
#   - M_RetabloOro2 / M_RetabloOro3: TextureSample de Retablo_GoldRough (lineal) con sampler "Color".
#     -> sampler LINEAR_COLOR.
#   - M_ConvPropLit: TextureSampleParameter2D con sampler "Normal" y textura por defecto de color.
#     -> textura por defecto /Engine/EngineMaterials/DefaultNormal (las instancias pueden sobreescribirla).
#   Recorre el grafo desde cada entrada del material (get_material_property_input_node + entradas).
#   Respaldo de los .uasset. Recompila y guarda.
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_materiales_android.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
MATS = {"/Game/JWN/Santos/M_RetabloOro2": "Content/JWN/Santos/M_RetabloOro2.uasset",
        "/Game/JWN/Santos/M_RetabloOro3": "Content/JWN/Santos/M_RetabloOro3.uasset",
        "/Game/JWN/Convento/M_ConvPropLit": "Content/JWN/Convento/M_ConvPropLit.uasset"}
MEL = unreal.MaterialEditingLibrary
PROPS = [unreal.MaterialProperty.MP_BASE_COLOR, unreal.MaterialProperty.MP_METALLIC, unreal.MaterialProperty.MP_SPECULAR,
         unreal.MaterialProperty.MP_ROUGHNESS, unreal.MaterialProperty.MP_NORMAL, unreal.MaterialProperty.MP_EMISSIVE_COLOR,
         unreal.MaterialProperty.MP_OPACITY, unreal.MaterialProperty.MP_OPACITY_MASK, unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,
         unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET]
res = {"err": None, "cambios": [], "nodos_textura": []}
try:
    default_normal = unreal.load_asset("/Engine/EngineMaterials/DefaultNormal")
    for path, rel in MATS.items():
        shutil.copy2(ROOT + "/" + rel, ROOT + "/Saved/ClaudeBackups/" + rel.split("/")[-1].replace(".uasset", "_pre_android.uasset"))
        m = unreal.load_asset(path)
        vistos = set(); pila = []
        for pr in PROPS:
            try:
                n = MEL.get_material_property_input_node(m, pr)
                if n: pila.append(n)
            except Exception:
                pass
        while pila:
            e = pila.pop()
            if e is None or e.get_name() in vistos: continue
            vistos.add(e.get_name())
            try:
                for x in MEL.get_inputs_for_material_expression(m, e):
                    if x: pila.append(x)
            except Exception:
                pass
            if isinstance(e, unreal.MaterialExpressionTextureSample):
                tex = e.get_editor_property("texture"); st = e.get_editor_property("sampler_type")
                info = [path.split("/")[-1], e.get_name(), tex.get_path_name() if tex else None, str(st), tex.get_editor_property("srgb") if tex else None]
                res["nodos_textura"].append(info)
                if tex and tex.get_name() == "Retablo_GoldRough" and st == unreal.MaterialSamplerType.SAMPLERTYPE_COLOR:
                    e.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
                    res["cambios"].append([path, e.get_name(), "sampler -> LINEAR_COLOR"])
                elif st == unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL and tex and tex.get_path_name().startswith("/Engine/EngineResources/DefaultTexture"):
                    e.set_editor_property("texture", default_normal)
                    res["cambios"].append([path, e.get_name(), "textura por defecto -> DefaultNormal"])
        MEL.recompile_material(m)
        res.setdefault("guardado", {})[path] = unreal.EditorAssetLibrary.save_asset(path, False)
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, default=str))
