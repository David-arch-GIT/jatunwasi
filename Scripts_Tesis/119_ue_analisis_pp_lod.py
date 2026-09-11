# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Reporta ajustes de PostProcess (bloom/AO/exposicion/motionblur) y meshes de alto poligono
#   sin LODs, para optimizar GPU sin cambiar el look.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/analisis_pp_lod.json"
res = {"ppv": [], "meshes_sin_lods": [], "meshes_altos": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    if "PostProcessVolume" in cn:
        try:
            s = a.get_editor_property("settings")
            info = {"label": a.get_actor_label()}
            for p in ["bloom_intensity", "bloom_method", "auto_exposure_method", "motion_blur_amount",
                      "ambient_occlusion_intensity", "scene_fringe_intensity", "vignette_intensity"]:
                try:
                    info[p] = str(getattr(s, p)) if hasattr(s, p) else "?"
                except Exception:
                    pass
            for ov in ["override_bloom_intensity", "override_motion_blur_amount", "override_ambient_occlusion_intensity"]:
                try:
                    info[ov] = bool(getattr(s, ov)) if hasattr(s, ov) else False
                except Exception:
                    pass
            res["ppv"].append(info)
        except Exception as e:
            res["ppv"].append({"err": str(e)[:80]})
# meshes altos + LODs (via componentes en el mapa, dedup por mesh)
seen = {}
for a in eas.get_all_level_actors():
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp.get_class().get_name() in ("InstancedStaticMeshComponent", "HierarchicalInstancedStaticMeshComponent"):
            continue
        m = comp.get_editor_property("static_mesh")
        if not m:
            continue
        nm = m.get_name()
        if nm in seen:
            continue
        try:
            tris = m.get_num_triangles(0)
            lods = m.get_num_lods() if hasattr(m, "get_num_lods") else (m.get_num_l_o_ds() if hasattr(m, "get_num_l_o_ds") else 1)
        except Exception:
            tris, lods = 0, 1
        seen[nm] = (tris, lods)
        if tris > 2000:
            res["meshes_altos"].append([nm, tris, lods])
            if lods <= 1:
                res["meshes_sin_lods"].append([nm, tris])
res["meshes_altos"].sort(key=lambda t: -t[1])
res["meshes_altos"] = res["meshes_altos"][:25]
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ANALISIS PP=%d meshes_altos=%d sin_lods=%d" % (len(res["ppv"]), len(res["meshes_altos"]), len(res["meshes_sin_lods"])))
