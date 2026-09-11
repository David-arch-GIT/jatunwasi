# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Re-evaluacion completa por zona: triangulos RENDERIZADOS (considerando min_lod),
#   caza "bombas" (assets con LOD renderizado > 8000 tris), luces visibles, y estima carga por zona.
#   Para confirmar que la escena este dentro del presupuesto Quest2 y no queden sorpresas.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reeval.json"
ZONES = {"plaza": (0,-1000), "hacienda": (-7000,-2500), "convento": (6500,5000), "templo": (0,11700)}
res = {"por_zona": {}, "bombas_restantes": [], "total_luces_visibles": 0, "err": []}
eas = unreal.EditorActorSubsystem()
cache = {}
def rendered_tris(m, comp):
    nm = m.get_name()
    try:
        ml = int(comp.get_editor_property("min_lod")) if comp.get_editor_property("override_min_lod") else 0
    except Exception:
        ml = 0
    key = (nm, ml)
    if key in cache: return cache[key]
    try:
        t = m.get_num_triangles(ml)
    except Exception:
        t = 0
    cache[key] = t
    return t
zdata = {z: {"tris_render": 0, "inst": 0, "luces": 0, "sm": 0} for z in ZONES}
allacts = eas.get_all_level_actors()
for a in allacts:
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    # asignar a la zona mas cercana dentro de 60m
    zone = None; best = 6000
    for z,(cx,cy) in ZONES.items():
        d = math.hypot(loc.x-cx, loc.y-cy)
        if d < best: best = d; zone = z
    if zone is None:
        continue
    zd = zdata[zone]
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent","SpotLightComponent") and lc.is_visible():
            zd["luces"] += 1; res["total_luces_visibles"] += 1
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        m = comp.get_editor_property("static_mesh")
        if not m: continue
        isinst = comp.get_class().get_name() in ("InstancedStaticMeshComponent","HierarchicalInstancedStaticMeshComponent")
        rt = rendered_tris(m, comp)
        cnt = comp.get_instance_count() if isinst else 1
        zd["tris_render"] += rt * cnt
        if isinst: zd["inst"] += cnt
        else: zd["sm"] += 1
        # bomba = LOD renderizado alto
        if rt > 8000:
            res["bombas_restantes"].append([a.get_actor_label(), m.get_name()[:28], rt, "x%d"%cnt, zone])
res["bombas_restantes"].sort(key=lambda x: -x[2]*(1 if x[3]=="x1" else int(x[3][1:])))
res["bombas_restantes"] = res["bombas_restantes"][:20]
for z in ZONES:
    zdata[z]["tris_render_M"] = round(zdata[z]["tris_render"]/1000000.0, 2)
res["por_zona"] = zdata
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("REEVAL done")
