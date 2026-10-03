# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Agrega a BP_CriaturaViva todas las variables expuestas (instance-editable) con tipo y default correcto,
#   y fija radios por defecto de SphereZona/SphereDeteccion en el CDO. Reporta cuales entraron.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bp_vars.json"
res = {"vars_ok": [], "vars_err": [], "cdo": [], "err": []}
PATH = "/Game/JWN/Blueprints/BP_CriaturaViva"
bp = unreal.EditorAssetLibrary.load_asset(PATH)
BEL = unreal.BlueprintEditorLibrary
def pin_float():
    t = unreal.EdGraphPinType()
    t.set_editor_property("pin_category", "real")
    t.set_editor_property("pin_sub_category", "float")
    return t
def pin_bool():
    t = unreal.EdGraphPinType(); t.set_editor_property("pin_category", "bool"); return t
def pin_obj(cls):
    t = unreal.EdGraphPinType()
    t.set_editor_property("pin_category", "object")
    t.set_editor_property("pin_sub_category_object", cls)
    return t
def pin_struct(struct):
    t = unreal.EdGraphPinType()
    t.set_editor_property("pin_category", "struct")
    t.set_editor_property("pin_sub_category_object", struct)
    return t
VARS = [
    ("RadioZona", pin_float, "500.0", True),
    ("VelMin", pin_float, "40.0", True),
    ("VelMax", pin_float, "110.0", True),
    ("PausaMin", pin_float, "2.0", True),
    ("PausaMax", pin_float, "7.0", True),
    ("DistDeteccion", pin_float, "350.0", True),
    ("ProbDeambular", pin_float, "0.6", True),
    ("bJugadorCerca", pin_bool, "false", False),
    ("CentroZona", lambda: pin_struct(unreal.load_object(None, "/Script/CoreUObject.Vector")), "", False),
    ("IdleAnim", lambda: pin_obj(unreal.AnimSequence.static_class()), "", True),
    ("WalkAnim", lambda: pin_obj(unreal.AnimSequence.static_class()), "", True),
    ("CriaturaMesh", lambda: pin_obj(unreal.SkeletalMesh.static_class()), "", True),
]
for name, mk, dv, inst in VARS:
    try:
        BEL.add_member_variable(bp, name, mk(), dv)
        if inst:
            BEL.set_blueprint_variable_instance_editable(bp, name, True)
        res["vars_ok"].append(name + (" [instancia]" if inst else " [interna]"))
    except Exception as e:
        res["vars_err"].append(name + ": " + str(e)[:50])
# compilar
try:
    BEL.compile_blueprint(bp)
except Exception as e:
    res["err"].append("compile:" + str(e)[:40])
# fijar radios en el CDO (default de los componentes)
try:
    cdo = unreal.get_default_object(bp.generated_class())
    for comp in cdo.get_components_by_class(unreal.SphereComponent):
        n = comp.get_name()
        if "Zona" in n:
            comp.set_editor_property("sphere_radius", 500.0)
            res["cdo"].append("SphereZona r=500")
        elif "Deteccion" in n:
            comp.set_editor_property("sphere_radius", 350.0)
            res["cdo"].append("SphereDeteccion r=350")
except Exception as e:
    res["err"].append("cdo:" + str(e)[:50])
try:
    BEL.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(PATH, only_if_is_dirty=False)
    res["pasos_final"] = "compilado+guardado"
except Exception as e:
    res["err"].append("save:" + str(e)[:40])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("BP VARS ok=%d err=%d" % (len(res["vars_ok"]), len(res["vars_err"])))
