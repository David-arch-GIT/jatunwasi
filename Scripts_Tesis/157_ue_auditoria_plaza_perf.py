# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-10
# Que hace: (UE) AUDITORIA DE RENDIMIENTO de la PLAZA (centro 0,-1000). Mide lo que causa lentitud al recorrer:
#   (1) draw calls aprox = componentes StaticMesh NO instanciados vs ISM/HISM. (2) luces MOVABLE con sombra (lo mas
#   caro en forward movil). (3) materiales translucidos/masked (overdraw). (4) actores movables. (5) meshes sin LODs.
#   Solo mide y escribe JSON, NO cambia nada. Radio 3500cm alrededor del centro de plaza.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_perf_audit.json"
CX, CY, R = 0.0, -1000.0, 3500.0
res = {"n_actores_radio": 0, "sm_individuales": 0, "ism_hism_comp": 0, "ism_instancias": 0,
       "luces_movable_sombra": [], "luces_movable_total": 0, "luces_static": 0,
       "mat_translucido": {}, "mat_masked": {}, "movables": 0, "meshes_sin_lod": {},
       "top_meshes_por_conteo": {}, "err": []}
eas = unreal.EditorActorSubsystem()
def dist2d(loc):
    return math.hypot(loc.x - CX, loc.y - CY)
mesh_count = {}
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if dist2d(loc) > R:
        continue
    res["n_actores_radio"] += 1
    # movabilidad
    try:
        root = a.root_component
        if root and str(root.get_editor_property("mobility")) == "ComponentMobility.MOVABLE":
            res["movables"] += 1
    except Exception:
        pass
    # luces
    for lc in a.get_components_by_class(unreal.LightComponent):
        try:
            mob = str(lc.get_editor_property("mobility"))
            casts = lc.get_editor_property("cast_shadows")
            if "MOVABLE" in mob:
                res["luces_movable_total"] += 1
                if casts:
                    res["luces_movable_sombra"].append(a.get_actor_label()[:30])
            elif "STATIC" in mob:
                res["luces_static"] += 1
        except Exception as e:
            res["err"].append("luz:" + str(e)[:30])
    # static meshes
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m:
                continue
            nm = m.get_name()
            is_inst = isinstance(c, unreal.InstancedStaticMeshComponent)
            if is_inst:
                res["ism_hism_comp"] += 1
                try:
                    res["ism_instancias"] += c.get_instance_count()
                except Exception:
                    pass
            else:
                res["sm_individuales"] += 1
                mesh_count[nm] = mesh_count.get(nm, 0) + 1
            # LODs
            try:
                nlod = m.get_num_lods()
                if nlod <= 1:
                    res["meshes_sin_lod"][nm] = res["meshes_sin_lod"].get(nm, 0) + 1
            except Exception:
                pass
            # materiales
            for mat in c.get_materials():
                if not mat:
                    continue
                try:
                    base = mat.get_base_material() if hasattr(mat, "get_base_material") else mat
                    bm = str(base.get_editor_property("blend_mode"))
                    mnm = base.get_name()
                    if "TRANSLUCENT" in bm or "ADDITIVE" in bm:
                        res["mat_translucido"][mnm] = res["mat_translucido"].get(mnm, 0) + 1
                    elif "MASKED" in bm:
                        res["mat_masked"][mnm] = res["mat_masked"].get(mnm, 0) + 1
                except Exception:
                    pass
        except Exception as e:
            res["err"].append("sm:" + str(e)[:30])
# top meshes individuales por conteo (candidatos a instanciar)
top = sorted(mesh_count.items(), key=lambda kv: -kv[1])[:20]
res["top_meshes_por_conteo"] = dict(top)
# resumir masked/translucido a totales
res["mat_masked_total"] = sum(res["mat_masked"].values())
res["mat_translucido_total"] = sum(res["mat_translucido"].values())
res["meshes_sin_lod_total"] = sum(res["meshes_sin_lod"].values())
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA AUDIT n=%d sm_ind=%d ism=%d movlight_shadow=%d" % (
    res["n_actores_radio"], res["sm_individuales"], res["ism_hism_comp"], len(res["luces_movable_sombra"])))
