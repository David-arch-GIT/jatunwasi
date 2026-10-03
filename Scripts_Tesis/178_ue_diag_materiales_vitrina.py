# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Diagnostica por que no se ve el habito: lista materiales (nombre + blend_mode) de la vitrina, el
#   maniqui y el habito; y si sus componentes StaticMesh estan visibles. Asi sabemos si el vidrio es transparente y si
#   el habito/maniqui renderizan.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_materiales.json"
res = {}
eas = unreal.EditorActorSubsystem()
def blend_of(mi):
    try:
        base = mi.get_base_material() if hasattr(mi, "get_base_material") else mi
        return str(base.get_editor_property("blend_mode")).split(".")[-1]
    except Exception:
        return "?"
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("VIT_Habito"):
        continue
    info = {"comps": []}
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        cd = {"visible": bool(c.get_editor_property("visible")), "mats": []}
        try:
            for i, mi in enumerate(c.get_materials()):
                if mi:
                    cd["mats"].append([mi.get_name(), blend_of(mi)])
                else:
                    cd["mats"].append(["NULL", "-"])
        except Exception as e:
            cd["err"] = str(e)[:30]
        info["comps"].append(cd)
    res[lab] = info
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG MATERIALES ok")
