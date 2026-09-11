# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) DIAGNOSTICO fino plaza: (1) por cada componente ISM/HISM en radio: mesh, #instancias, cull_end actual,
#   si es follaje masked. (2) las 13 luces movable: label, intensidad, atten_radius, max_draw_distance actual.
#   (3) que son los 26 Plane (label + material). Solo mide, escribe JSON. Para decidir cull/culling de luces.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_diag2.json"
CX, CY, R = 0.0, -1000.0, 3500.0
res = {"foliage": [], "luces": [], "planes": [], "err": []}
eas = unreal.EditorActorSubsystem()
def d2(loc): return math.hypot(loc.x - CX, loc.y - CY)
FOL = ["grass","fern","clover","moss","flower","shrub","bush","plant","leaf","foliage","maple","palm","tree","impostor","billboard"]
for a in eas.get_all_level_actors():
    try: loc = a.get_actor_location()
    except Exception: continue
    if d2(loc) > R: continue
    lab = a.get_actor_label()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name()
            is_inst = isinstance(c, unreal.InstancedStaticMeshComponent)
            if is_inst:
                try: ncnt = c.get_instance_count()
                except Exception: ncnt = -1
                try:
                    cs = c.get_editor_property("instance_start_cull_distance")
                    ce = c.get_editor_property("instance_end_cull_distance")
                except Exception:
                    cs = ce = -1
                if ncnt >= 40:  # solo los densos
                    res["foliage"].append({"lab": lab[:24], "mesh": nm[:26], "n": ncnt, "cull_end": ce})
            if nm == "Plane":
                mats = [ (mm.get_name()[:22] if mm else "None") for mm in c.get_materials() ]
                vis = c.get_editor_property("visible")
                res["planes"].append({"lab": lab[:26], "mat": mats[:2], "vis": vis})
        except Exception as e:
            res["err"].append("sm:" + str(e)[:30])
    for lc in a.get_components_by_class(unreal.LightComponent):
        try:
            mob = str(lc.get_editor_property("mobility"))
            if "MOVABLE" not in mob: continue
            inten = lc.get_editor_property("intensity")
            try: att = lc.get_editor_property("attenuation_radius")
            except Exception: att = -1
            try: mdd = lc.get_editor_property("max_draw_distance")
            except Exception: mdd = -1
            res["luces"].append({"lab": lab[:26], "int": round(inten,1), "att": round(att), "mdd": round(mdd)})
        except Exception as e:
            res["err"].append("luz:" + str(e)[:30])
# resumen
res["foliage"] = sorted(res["foliage"], key=lambda x: -x["n"])[:25]
res["n_planes"] = len(res["planes"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG2 fol=%d luces=%d planes=%d" % (len(res["foliage"]), len(res["luces"]), len(res["planes"])))
