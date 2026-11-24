# 430_ue_relieve_deshacer_acomodo.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: DESHACER exactamente el acomodo de vegetacion hecho por 421 (resta a cada instancia la
#   altura dz guardada en relieve_snap_undo.json, por actor|componente e indice). Paso previo a
#   regenerar el relieve v5 (mas alejado del pueblo). Verifica que el numero de instancias coincida.
import unreal, json, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/relieve_undo_res.json"
res = {"err": None, "restored": 0, "mismatch": []}
try:
    undo = json.load(open(ROOT + "/Saved/ClaudeBackups/relieve_snap_undo.json"))
    comps = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            comps[a.get_actor_label() + "|" + c.get_name()] = c
    for key, dz in undo.items():
        c = comps.get(key)
        if c is None or c.get_instance_count() != len(dz):
            res["mismatch"].append([key, None if c is None else c.get_instance_count(), len(dz)]); continue
        last = max([k for k, v in enumerate(dz) if v > 0], default=-1)
        for k, v in enumerate(dz):
            if v > 0:
                t = c.get_instance_transform(k, True)
                t.translation = unreal.Vector(t.translation.x, t.translation.y, t.translation.z - v)
                c.update_instance_transform(k, t, True, k == last, True)
                res["restored"] += 1
    if not res["mismatch"]:
        import os
        os.replace(ROOT + "/Saved/ClaudeBackups/relieve_snap_undo.json", ROOT + "/Saved/ClaudeBackups/relieve_snap_undo_v1_aplicado.json")
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
