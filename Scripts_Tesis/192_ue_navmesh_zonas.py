# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Verifica que cada zona de criatura tenga NavMesh (via random reachable point). Donde falte, spawnea un
#   NavMeshBoundsVolume centrado (radio ~700). Ajusta radios del BP. Reporta cobertura. (Rebuild de nav puede requerir
#   Build>Build Paths en el editor.)
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/navmesh_zonas.json"
res = {"cobertura": {}, "volumenes_nuevos": [], "bp_radios": [], "err": []}
w = unreal.EditorLevelLibrary.get_editor_world()
nav = unreal.NavigationSystemV1.get_navigation_system(w)
ZONAS = {
    "Karisiri": (5890.0, 4810.0, 15.0),
    "Condenado": (6510.0, 5390.0, 15.0),
    "Duende": (-4021.0, 807.0, -5.0),
}
def tiene_nav(x, y, z):
    try:
        r = unreal.NavigationSystemV1.k2_get_random_reachable_point_in_radius(w, unreal.Vector(x, y, z), 300.0)
        # devuelve (bool, Vector) o Vector segun version
        if isinstance(r, tuple):
            return bool(r[0])
        return r is not None
    except Exception as e:
        res["err"].append("navcheck:" + str(e)[:40])
        return False
eas = unreal.EditorActorSubsystem()
for nombre, (x, y, z) in ZONAS.items():
    ok = tiene_nav(x, y, z)
    res["cobertura"][nombre] = "SI" if ok else "NO"
    if not ok:
        try:
            vol = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(x, y, z + 100))
            vol.set_actor_label("CRIA_Nav_" + nombre)
            vol.set_actor_scale3d(unreal.Vector(14.0, 14.0, 6.0))  # ~ 1400x1400x600 (cubo base 100)
            res["volumenes_nuevos"].append(nombre + " nav agregado")
        except Exception as e:
            res["err"].append("spawnvol " + nombre + ":" + str(e)[:40])
# ajustar radios del BP (default components)
try:
    bp = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/BP_CriaturaViva")
    cdo = unreal.get_default_object(bp.generated_class())
    for comp in cdo.get_components_by_class(unreal.SphereComponent):
        n = comp.get_name()
        if "Zona" in n: comp.set_editor_property("sphere_radius", 500.0); res["bp_radios"].append("Zona=500")
        elif "Deteccion" in n: comp.set_editor_property("sphere_radius", 350.0); res["bp_radios"].append("Deteccion=350")
except Exception as e:
    res["err"].append("bpradio:" + str(e)[:40])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("NAVMESH ZONAS ok")
