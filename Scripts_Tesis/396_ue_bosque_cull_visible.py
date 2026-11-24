# 396_ue_bosque_cull_visible.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: los campos se veian vacios porque PCG_BosqueVol cortaba arboles/arbustos
#   a 22 m (cull 1500-2200). Se amplia el corte de ARBOLES a 60 m forzando MinLOD 2
#   (LOD liviano; LOD3 es impostor de 9 vertices) y ARBUSTOS a 35 m (MinLOD 1).
#   Sin sombras. Guarda valores previos en JSON para poder revertir.
# NOTA: si PCG_BosqueVol se regenera, estos valores se pierden (reaplicar este script).
import unreal, json, traceback

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bosque_cull_prev.json"
res = {"changed": [], "err": None}
TREE_KEYS = ("Tree", "Maple", "Oak", "Pine")
BUSH_KEYS = ("Bush", "Plant")
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lbl = a.get_actor_label()
        if lbl not in ("PCG_BosqueVol", "PCG_RelieveVol"):
            continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            sm = c.get_editor_property("static_mesh"); n = sm.get_name() if sm else ""
            prev = [c.get_editor_property("instance_start_cull_distance"),
                    c.get_editor_property("instance_end_cull_distance"),
                    c.get_editor_property("override_min_lod"), c.get_editor_property("min_lod")]
            if any(k in n for k in TREE_KEYS):
                cs, ce, ml = 4500, 6000, 2
            elif any(k in n for k in BUSH_KEYS):
                cs, ce, ml = 2800, 3500, 1
            else:
                continue
            c.set_editor_property("instance_start_cull_distance", cs)
            c.set_editor_property("instance_end_cull_distance", ce)
            c.set_editor_property("override_min_lod", True)
            c.set_editor_property("min_lod", ml)
            c.set_editor_property("cast_shadow", False)
            res["changed"].append([lbl, c.get_name(), n, c.get_instance_count(), prev, [cs, ce, ml]])
    unreal.EditorLevelLibrary.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:600]
open(OUT, "w").write(json.dumps(res, indent=1))
