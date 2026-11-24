# 410_ue_inventario_fuente_puertas_piso.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: INVENTARIO (solo lectura) para la nueva ronda: (1) fuente de la plaza (actor colocado,
#   malla, triangulos por LOD, materiales y tamano de texturas; versiones Tripo FuenteLimpia/Fix/Fix2),
#   (2) puertas existentes (BP_AutoDoor y mallas Door en el nivel), (3) piso Ground_Cochabamba
#   (malla, material, escala), (4) sonidos ambiente (AMB_*/NOCHE_*/Snd_*) para el interruptor.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inv410.json"
res = {"err": None}
def mesh_info(sm):
    d = {"path": sm.get_path_name(), "lods": []}
    for l in range(sm.get_num_lods()):
        d["lods"].append(sm.get_num_triangles(l))
    mats = []
    for i, m in enumerate(sm.static_materials):
        mi = m.material_interface
        texs = []
        if mi:
            try:
                for t in unreal.MaterialEditingLibrary.get_used_textures(mi):
                    texs.append([t.get_name(), t.blueprint_get_size_x(), t.blueprint_get_size_y()])
            except Exception:
                pass
        mats.append([str(m.material_slot_name), mi.get_path_name() if mi else None, texs])
    d["mats"] = mats
    b = sm.get_bounding_box(); d["size"] = [round(b.max.x - b.min.x), round(b.max.y - b.min.y), round(b.max.z - b.min.z)]
    return d
try:
    res["fountain_actors"] = []; res["doors"] = []; res["ground"] = []; res["sounds"] = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label(); low = lb.lower(); L = a.get_actor_location()
        p = [round(L.x), round(L.y), round(L.z)]
        cls = a.get_class().get_name()
        if "fountain" in low or "fuente" in low:
            d = {"label": lb, "loc": p, "hidden": a.is_hidden_ed(), "scale": str(a.get_actor_scale3d()), "rot": str(a.get_actor_rotation())}
            sm = a.get_component_by_class(unreal.StaticMeshComponent)
            if sm and sm.static_mesh:
                d["mesh"] = mesh_info(sm.static_mesh)
            res["fountain_actors"].append(d)
        if "door" in low or "puerta" in low or "door" in cls.lower():
            res["doors"].append([lb, cls, p, str(a.get_actor_rotation())])
        if lb.startswith("Ground") or "ground" in low:
            sm = a.get_component_by_class(unreal.StaticMeshComponent)
            res["ground"].append([lb, p, str(a.get_actor_scale3d()), sm.static_mesh.get_path_name() if sm and sm.static_mesh else None,
                                  [m.get_path_name() if m else None for m in (sm.get_materials() if sm else [])]])
        if isinstance(a, unreal.AmbientSound):
            ac = a.get_editor_property("audio_component"); s = ac.get_editor_property("sound")
            res["sounds"].append([lb, s.get_path_name() if s else None])
    res["tripo"] = []
    for path in ("/Game/JWN/TripoClean2/FuenteLimpia/FuenteLimpia", "/Game/JWN/TripoClean2/FuenteFix2/FuenteFix2",
                 "/Game/JWN/TripoClean2/FuenteFix/FuenteFix", "/Game/JWN/TripoClean2/fuente_plaza_mejorado/StaticMeshes/fuente_plaza_mejorado"):
        sm = unreal.load_asset(path)
        if sm:
            res["tripo"].append(mesh_info(sm))
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))
