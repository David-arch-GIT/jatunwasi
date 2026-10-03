import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/canvas_mat.json"
res = {"MI_JW_CanvasA": {}, "parent_expr": [], "M_FotoAntano_expr": []}

def dump_mat_expressions(matpath, key):
    m = unreal.EditorAssetLibrary.load_asset(matpath)
    if not m: return None
    out = []
    try:
        exprs = unreal.MaterialEditingLibrary.get_material_expressions(m) if hasattr(unreal.MaterialEditingLibrary,"get_material_expressions") else []
    except Exception:
        exprs = []
    for e in exprs:
        cn = e.get_class().get_name()
        d = {"type": cn}
        # parametros comunes
        for prop in ["parameter_name","u_tiling","v_tiling","coordinate_index","const","r","g","b","a"]:
            try:
                v = e.get_editor_property(prop)
                d[prop] = str(v)
            except Exception:
                pass
        out.append(d)
    res[key] = out
    return m.get_name()

# 1) MI_JW_CanvasA: parent + parametros escalares/vectores/texturas
mi = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Materials/MI_JW_CanvasA")
if not mi:
    # buscar por nombre en todo el content
    for a in unreal.EditorAssetLibrary.list_assets("/Game", recursive=True):
        if "MI_JW_CanvasA" in a:
            mi = unreal.EditorAssetLibrary.load_asset(a.split(".")[0]); break
if mi:
    res["MI_JW_CanvasA"]["path"] = mi.get_path_name()
    try:
        par = mi.get_editor_property("parent")
        res["MI_JW_CanvasA"]["parent"] = par.get_path_name() if par else None
    except Exception as e:
        res["MI_JW_CanvasA"]["parent_err"] = str(e)[:60]
    # scalar params
    try:
        for sp in mi.get_editor_property("scalar_parameter_values"):
            res["MI_JW_CanvasA"].setdefault("scalars",[]).append(str(sp.parameter_info.name)+"="+str(sp.parameter_value))
    except Exception: pass
    try:
        for tp in mi.get_editor_property("texture_parameter_values"):
            t = tp.parameter_value
            res["MI_JW_CanvasA"].setdefault("textures",[]).append(str(tp.parameter_info.name)+"="+(t.get_name() if t else "None"))
    except Exception: pass
    # parent expressions
    if par: dump_mat_expressions(par.get_path_name(), "parent_expr")
# 2) M_FotoAntano expr
dump_mat_expressions("/Game/FotosAntano/M_FotoAntano", "M_FotoAntano_expr")
open(OUT,"w").write(json.dumps(res, indent=1))
