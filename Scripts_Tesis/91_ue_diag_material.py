# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) DIAGNOSTICO LIGERO (sin crear/borrar/recompilar materiales). Reporta parent y BaseTex de cada MI,
#           material asignado a cada AppSK, y fuerza el condenado visible (PulseBiasNeg alto = op ligera) para captura.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_mat.json"
res = {"mis": [], "actors": [], "err": []}
mel = unreal.MaterialEditingLibrary
for label in ["Hac_Duende","Plz_Duende","Conv_Condenado","Conv_Karisiri"]:
    p = "/Game/JWN/Apariciones/MI_Fant_" + label
    try:
        if not unreal.EditorAssetLibrary.does_asset_exist(p):
            res["mis"].append({"mi": label, "existe": False}); continue
        mi = unreal.load_asset(p)
        par = mi.get_editor_property("parent")
        tex = mel.get_material_instance_texture_parameter_value(mi, "BaseTex")
        res["mis"].append({"mi": label, "parent": (par.get_name() if par else None),
                           "baseTex": (tex.get_name() if tex else None)})
    except Exception as e:
        res["err"].append("mi %s: %s" % (label, e))
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if l.startswith("AppSK_"):
        try:
            comp = a.skeletal_mesh_component
            m = comp.get_material(0)
            res["actors"].append({"label": l, "mat": (m.get_name() if m else None)})
        except Exception as e:
            res["err"].append("act %s: %s" % (l, e))
# forzar condenado visible (op ligera de MI, sin recompilar master)
try:
    mic = unreal.load_asset("/Game/JWN/Apariciones/MI_Fant_Conv_Condenado")
    mel.set_material_instance_scalar_parameter_value(mic, "PulseBiasNeg", 1.8)
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Apariciones/MI_Fant_Conv_Condenado")
    res["forzado"] = "condenado visible"
except Exception as e:
    res["err"].append("forzar: %s" % e)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG MAT done")
