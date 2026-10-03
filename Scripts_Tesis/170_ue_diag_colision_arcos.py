# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) DIAGNOSTICO de colision de los ARCOS del convento. Por cada mesh con "arch" en el nombre usado en la
#   escena: reporta collision_trace_flag (Default/SimpleAndComplex/ComplexAsSimple/SimpleAsComplex), cuantas primitivas
#   simples tiene (box/convex/sphere/sphyl), tris LOD0 (costo si complex), y perfil de colision del componente. Ademas
#   revisa si hay FOLLAJE con colision cerca de los arcos (la causa real del bloqueo la vez pasada). Solo mide.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_arcos.json"
res = {"arcos_mesh": {}, "arcos_en_escena": [], "follaje_con_colision_cerca": [], "err": []}
eas = unreal.EditorActorSubsystem()
TRACE = {0: "CTF_UseDefault(Project)", 1: "CTF_UseSimpleAndComplex", 2: "CTF_UseComplexAsSimple", 3: "CTF_UseSimpleAsComplex"}
def describe_mesh(m):
    d = {}
    try:
        bs = m.get_editor_property("body_setup")
        if bs:
            tf = bs.get_editor_property("collision_trace_flag")
            d["trace_flag"] = TRACE.get(int(tf), str(tf))
            ag = bs.get_editor_property("agg_geom")
            d["box"] = len(ag.get_editor_property("box_elems"))
            d["convex"] = len(ag.get_editor_property("convex_elems"))
            d["sphere"] = len(ag.get_editor_property("sphere_elems"))
            d["sphyl"] = len(ag.get_editor_property("sphyl_elems"))
            d["prim_simples_total"] = d["box"] + d["convex"] + d["sphere"] + d["sphyl"]
        else:
            d["trace_flag"] = "SIN body_setup"
    except Exception as e:
        d["err"] = str(e)[:40]
    try: d["tris_lod0"] = m.get_num_triangles(0)
    except Exception: pass
    return d
# arcos en escena
arch_locs = []
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name()
            if "arch" not in nm.lower(): continue
            loc = a.get_actor_location()
            arch_locs.append((loc.x, loc.y, loc.z))
            if nm not in res["arcos_mesh"]:
                res["arcos_mesh"][nm] = describe_mesh(m)
            # perfil de colision del componente
            prof = c.get_collision_profile_name()
            ce = str(c.get_collision_enabled()).split(".")[-1]
            res["arcos_en_escena"].append({"actor": a.get_actor_label()[:24], "mesh": nm, "perfil": str(prof), "col": ce})
        except Exception as e:
            res["err"].append(str(e)[:36])
# follaje con colision cerca de algun arco (radio 500)
import math
FOL = ["grass","fern","clover","bush","plant","flower","shrub","moss","leaf"]
def near_arch(loc):
    for (x,y,z) in arch_locs:
        if math.hypot(loc.x-x, loc.y-y) < 700 and abs(loc.z-z) < 500:
            return True
    return False
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name().lower()
            if not any(k in nm for k in FOL): continue
            ce = str(c.get_collision_enabled()).split(".")[-1]
            if "NO_COLLISION" in ce: continue
            loc = a.get_actor_location()
            if near_arch(loc):
                res["follaje_con_colision_cerca"].append({"actor": a.get_actor_label()[:20], "mesh": m.get_name(), "col": ce})
        except Exception:
            pass
res["n_arcos_escena"] = len(res["arcos_en_escena"])
res["n_follaje_bloq"] = len(res["follaje_con_colision_cerca"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG ARCOS meshes=%d escena=%d follaje_bloq=%d" % (len(res["arcos_mesh"]), len(res["arcos_en_escena"]), len(res["follaje_con_colision_cerca"])))
