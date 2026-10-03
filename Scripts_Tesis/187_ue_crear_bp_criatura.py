# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Crea BP_CriaturaViva (padre Character) + componentes SphereDeteccion y SphereZona (sus radios = params
#   expuestos nativos por instancia). Testea si el puente puede AGREGAR variables al BP. Compila y guarda. Reporta que
#   funciono y que no (para saber que me falta cablear a mano).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bp_criatura.json"
res = {"pasos": [], "err": [], "vars_test": {}}
PKG = "/Game/JWN/Blueprints"
NAME = "BP_CriaturaViva"
at = unreal.AssetToolsHelpers.get_asset_tools()
# 1) crear BP
try:
    if unreal.EditorAssetLibrary.does_asset_exist(PKG + "/" + NAME):
        bp = unreal.EditorAssetLibrary.load_asset(PKG + "/" + NAME)
        res["pasos"].append("BP ya existia, cargado")
    else:
        fac = unreal.BlueprintFactory()
        fac.set_editor_property("parent_class", unreal.Character)
        bp = at.create_asset(NAME, PKG, unreal.Blueprint, fac)
        res["pasos"].append("BP creado (padre Character)")
except Exception as e:
    res["err"].append("crearBP:" + str(e)[:60]); bp = None
# 2) agregar componentes via SubobjectDataSubsystem
def add_comp(bp, comp_class, comp_name):
    try:
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        handles = sds.k2_gather_subobject_data_for_blueprint(bp)
        root = handles[0]
        params = unreal.AddNewSubobjectParams()
        params.set_editor_property("parent_handle", root)
        params.set_editor_property("new_class", comp_class)
        params.set_editor_property("blueprint_context", bp)
        h, fail = sds.add_new_subobject(params)
        if fail and str(fail):
            res["err"].append("addcomp %s: %s" % (comp_name, str(fail)[:40]))
            return None
        sds.rename_subobject(h, comp_name)
        res["pasos"].append("comp %s agregado" % comp_name)
        return h
    except Exception as e:
        res["err"].append("addcomp %s: %s" % (comp_name, str(e)[:50]))
        return None
if bp:
    add_comp(bp, unreal.SphereComponent, "SphereDeteccion")
    add_comp(bp, unreal.SphereComponent, "SphereZona")
# 3) TEST agregar variable (varias vias)
if bp:
    try:
        unreal.BlueprintEditorLibrary.add_member_variable(bp, "VelMin", unreal.EdGraphPinType())  # probablemente no exista
        res["vars_test"]["BlueprintEditorLibrary.add_member_variable"] = "OK?"
    except Exception as e:
        res["vars_test"]["BlueprintEditorLibrary.add_member_variable"] = "NO: " + str(e)[:50]
    # metodos disponibles en BlueprintEditorLibrary
    try:
        res["vars_test"]["metodos_BEL"] = [m for m in dir(unreal.BlueprintEditorLibrary) if "var" in m.lower() or "member" in m.lower()]
    except Exception as e:
        res["vars_test"]["metodos_BEL"] = str(e)[:40]
# 4) compilar + guardar
if bp:
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_asset(PKG + "/" + NAME, only_if_is_dirty=False)
        res["pasos"].append("compilado + guardado")
    except Exception as e:
        res["err"].append("compilar:" + str(e)[:50])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("BP CRIATURA pasos=%d err=%d" % (len(res["pasos"]), len(res["err"])))
