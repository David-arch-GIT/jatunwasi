# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Agrega variables a BP_CriaturaViva con add_member_variable(bp,name,type) (3 args), marca instance-
#   editable, y fija defaults via el CDO. Fija radios de esferas. Compila y guarda. Reporta.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bp_vars3.json"
res = {"vars_ok": [], "vars_err": [], "defaults": [], "cdo": [], "err": []}
PATH = "/Game/JWN/Blueprints/BP_CriaturaViva"
bp = unreal.EditorAssetLibrary.load_asset(PATH)
BEL = unreal.BlueprintEditorLibrary
def tfloat(): return BEL.get_basic_type_by_name("float")
def tbool(): return BEL.get_basic_type_by_name("bool")
def tanim(): return BEL.get_object_reference_type(unreal.AnimSequence.static_class())
def tskel(): return BEL.get_object_reference_type(unreal.SkeletalMesh.static_class())
def tvec(): return BEL.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector"))
VARS = [
    ("RadioZona", tfloat, 500.0, True),
    ("VelMin", tfloat, 40.0, True),
    ("VelMax", tfloat, 110.0, True),
    ("PausaMin", tfloat, 2.0, True),
    ("PausaMax", tfloat, 7.0, True),
    ("DistDeteccion", tfloat, 350.0, True),
    ("ProbDeambular", tfloat, 0.6, True),
    ("bJugadorCerca", tbool, False, False),
    ("CentroZona", tvec, None, False),
    ("IdleAnim", tanim, None, True),
    ("WalkAnim", tanim, None, True),
    ("CriaturaMesh", tskel, None, True),
]
for name, mk, dv, inst in VARS:
    try:
        BEL.add_member_variable(bp, name, mk())
        if inst:
            BEL.set_blueprint_variable_instance_editable(bp, name, True)
        res["vars_ok"].append(name + (" [inst]" if inst else " [int]"))
    except Exception as e:
        res["vars_err"].append(name + ": " + str(e)[:55])
try: BEL.compile_blueprint(bp)
except Exception as e: res["err"].append("compile1:" + str(e)[:30])
# defaults + radios via CDO
try:
    cdo = unreal.get_default_object(bp.generated_class())
    for name, mk, dv, inst in VARS:
        if dv is None: continue
        for cand in [name, name.lower()]:
            try:
                cdo.set_editor_property(cand, dv); res["defaults"].append("%s=%s" % (name, dv)); break
            except Exception as e:
                if cand == name.lower(): res["vars_err"].append("def %s: %s" % (name, str(e)[:30]))
    for comp in cdo.get_components_by_class(unreal.SphereComponent):
        n = comp.get_name()
        if "Zona" in n: comp.set_editor_property("sphere_radius", 500.0); res["cdo"].append("Zona=500")
        elif "Deteccion" in n: comp.set_editor_property("sphere_radius", 350.0); res["cdo"].append("Deteccion=350")
except Exception as e:
    res["err"].append("cdo:" + str(e)[:50])
try:
    BEL.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset(PATH, only_if_is_dirty=False)
    res["final"] = "guardado"
except Exception as e:
    res["err"].append("save:" + str(e)[:40])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("BP VARS3 ok=%d err=%d" % (len(res["vars_ok"]), len(res["vars_err"])))
