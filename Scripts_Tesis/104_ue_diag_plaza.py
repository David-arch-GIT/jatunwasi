# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) DIAGNOSTICO SOLO-LECTURA de la zona PLAZA (centro ~0,-1000 cm). Reporta que es lo pesado:
#   luces, componentes de instancias (con conteo), y meshes estaticos grandes. NO modifica nada. Liviano.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_plaza.json"
CX, CY, R = 0.0, -1000.0, 6000.0   # radio 60m alrededor del centro de la plaza
res = {"lights": 0, "ism_comps": 0, "ism_instances": 0, "sm_comps": 0,
       "top_ism": [], "top_sm": [], "light_labels": []}
eas = unreal.EditorActorSubsystem()
ism_list = []
sm_list = []
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    d = math.hypot(loc.x - CX, loc.y - CY)
    if d > R:
        continue
    lbl = a.get_actor_label()
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            res["lights"] += 1
            if len(res["light_labels"]) < 30:
                res["light_labels"].append(lbl)
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        n = comp.get_instance_count()
        res["ism_comps"] += 1
        res["ism_instances"] += n
        ism_list.append((lbl, n))
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp.get_class().get_name() in ("InstancedStaticMeshComponent", "HierarchicalInstancedStaticMeshComponent"):
            continue
        res["sm_comps"] += 1
        sm_list.append((lbl, 1))
ism_list.sort(key=lambda t: -t[1])
res["top_ism"] = ism_list[:20]
# agrupar SM por label-prefijo para ver cuantos de cada tipo
from collections import Counter
cnt = Counter([l for (l, _) in sm_list])
res["top_sm"] = cnt.most_common(20)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG PLAZA lights=%d ism_comps=%d ism_inst=%d sm=%d" % (res["lights"], res["ism_comps"], res["ism_instances"], res["sm_comps"]))
