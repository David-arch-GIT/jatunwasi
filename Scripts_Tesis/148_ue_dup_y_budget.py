# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Solo LEE. (1) Detecta StaticMeshActors DUPLICADOS/encimados (misma malla + misma ubicacion ~50cm) que
#   dibujan doble. (2) Re-audita triangulos por zona (SMA, LOD0) para confirmar presupuesto. Ayuda a hallar ganancias
#   seguras (quitar duplicados) sin tocar nada visible.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dup_budget.json"
res = {"duplicados": [], "n_dup_extra": 0, "tris_por_zona": {}, "top_tris": [], "err": []}
eas = unreal.EditorActorSubsystem()
ZONAS = {"plaza":(0,-1000), "hacienda":(-7000,-2500), "convento":(6200,5100), "templo":(50,12155)}
def zona_de(x,y):
    best=None; bd=1e18
    for z,(zx,zy) in ZONAS.items():
        d=math.hypot(x-zx,y-zy)
        if d<bd: bd=d; best=z
    return best if bd<6000 else "otros"
seen = {}
ztris = {k:0 for k in list(ZONAS.keys())+["otros"]}
alltris = []
for a in eas.get_all_level_actors():
    if a.get_class().get_name()!="StaticMeshActor": continue
    try:
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if not smc: continue
        m = smc.get_editor_property("static_mesh")
        if not m: continue
        loc = a.get_actor_location()
        key = (m.get_name(), round(loc.x/50), round(loc.y/50), round(loc.z/50))
        if key in seen:
            seen[key].append(a.get_actor_label()); res["n_dup_extra"]+=1
        else:
            seen[key]=[a.get_actor_label()]
        # tris a LOD0 (peor caso visible de cerca)
        try:
            t0 = m.get_num_triangles(0)
        except Exception:
            t0 = 0
        z = zona_de(loc.x, loc.y)
        ztris[z]+=t0
        alltris.append((t0, a.get_actor_label()[:24], m.get_name()[:24]))
    except Exception as e:
        res["err"].append(str(e)[:40])
for key,labels in seen.items():
    if len(labels)>1:
        res["duplicados"].append([key[0], [round(key[1]*50),round(key[2]*50),round(key[3]*50)], labels])
alltris.sort(reverse=True)
res["top_tris"]=[[t,l,m] for t,l,m in alltris[:20]]
res["tris_por_zona"]={k:round(v) for k,v in ztris.items()}
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("DUP BUDGET dup=%d" % res["n_dup_extra"])
