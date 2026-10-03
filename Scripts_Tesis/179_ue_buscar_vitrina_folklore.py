# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Busca en el nivel una vitrina del folklore YA montada (mesh KitFolklore_SM_HF_VitrinaTall o VitrinaLow)
#   y lee sus overrides de material por slot, para copiarlos a la vitrina del habito. Reporta label + materiales.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vitrina_folklore_mats.json"
res = {"encontradas": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith("VIT_Habito"):
        continue
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if not m:
            continue
        nm = m.get_name()
        if "Vitrina" not in nm:
            continue
        mats = []
        try:
            for i, mi in enumerate(c.get_materials()):
                mats.append(mi.get_path_name() if mi else "NULL")
        except Exception as e:
            res["err"].append(str(e)[:30])
        res["encontradas"].append({"actor": lab[:26], "mesh": nm, "mats": mats})
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("VITRINA FOLKLORE n=%d" % len(res["encontradas"]))
