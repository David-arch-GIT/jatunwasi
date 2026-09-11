# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) ARREGLO NAVEGACION. Quita colision a la vegetacion decorativa (pasto/helecho/trebol/musgo/flor/
#   arbusto/planta) en TODO el mapa. Esa colision a la altura de los pies era lo que bloqueaba avanzar (no los arcos).
#   Las plantas siguen viendose (solo dejan de chocar). Mantiene colision en arboles/tocones/roca/muro/columna/arco.
#   ISM y StaticMesh. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/follaje_nocol.json"
res = {"tocados": 0, "por_mesh": {}, "err": []}
FOLIAGE = ["grass","fern","clover","moss","flower","amaryllis","hydrangea","boxwood","elderberry",
           "shrub","bush","forestplant","bigleaf","_plant","plant_"]
KEEP = ["tree","oak","maple","tropical","stump","trunk","rock","stone","wall","column","arch"]
eas = unreal.EditorActorSubsystem()
def is_foliage(nm):
    low = nm.lower()
    if any(k in low for k in KEEP): return False
    return any(k in low for k in FOLIAGE)
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):  # incluye ISM (subclase)
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name()
            if not is_foliage(nm): continue
            ce = c.get_collision_enabled()
            if str(ce).split(".")[-1].startswith("NO_COLLISION"): continue
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            res["tocados"] += 1
            res["por_mesh"][nm] = res["por_mesh"].get(nm,0)+1
        except Exception as e:
            res["err"].append(str(e)[:40])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("FOLLAJE NOCOL %d" % res["tocados"])
