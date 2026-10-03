# Barrido global: cualquier componente con material EFECTIVO = WorldGrid/Default/None (bug visual blanco/grilla).
# Efectivo = override[i] si existe, si no el default del mesh. Solo cuenta lo que se VE (visible, no hidden).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/scan_grid.json"
res={"bugs":[], "total_comps":0, "visibles_revisados":0}
BAD={"WorldGridMaterial","DefaultMaterial","BasicShapeMaterial","M_Default","DefaultDeferredDecalMaterial"}
eas=unreal.EditorActorSubsystem()
def eff_mats(c):
    sm=c.get_editor_property("static_mesh")
    if not sm: return []
    try: statmats=sm.get_editor_property("static_materials")
    except Exception: statmats=[]
    ov=c.get_editor_property("override_materials")
    out=[]
    n=max(len(statmats), len(ov))
    for i in range(n):
        m=None
        if i < len(ov) and ov[i]: m=ov[i]
        elif i < len(statmats):
            try: m=statmats[i].get_editor_property("material_interface")
            except Exception: m=None
        out.append(m)
    return out
for a in eas.get_all_level_actors():
    hidden = False
    try: hidden = a.get_editor_property("is_temporarily_hidden_in_editor") or a.get_editor_property("hidden")
    except Exception: pass
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        res["total_comps"]+=1
        # visibilidad del componente
        try:
            vis = c.get_editor_property("visible")
            hig = c.get_editor_property("hidden_in_game")
        except Exception:
            vis=True; hig=False
        if hig or not vis:
            continue
        res["visibles_revisados"]+=1
        for i,m in enumerate(eff_mats(c)):
            nm = m.get_name() if m else "None"
            if (m is None) or (nm in BAD):
                sm=c.get_editor_property("static_mesh")
                res["bugs"].append({"actor":a.get_actor_label()[:38],"mesh":(sm.get_name() if sm else "?"),"slot":i,"mat":nm,"clase":a.get_class().get_name()})
res["n_bugs"]=len(res["bugs"])
# agrupar por mesh para resumen
grp={}
for b in res["bugs"]:
    k=b["mesh"]+" | "+b["mat"]
    grp[k]=grp.get(k,0)+1
res["resumen"]=grp
res["bugs"]=res["bugs"][:40]
open(OUT,"w").write(json.dumps(res,indent=1))
