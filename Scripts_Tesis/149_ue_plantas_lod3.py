# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Baja a min_lod=3 los actores de plantas de FONDO con LOD-bomba (boxwood y hortensia big-leaf), que ya
#   estaban en LOD2. Boxwood LOD2 15418->LOD3 6992; hortensia LOD2 11581->LOD3 3630. Reversible. Cero impacto visual
#   relevante (plantas de jardin de fondo). NO toca santos/retablo/arquitectura (hero, quedan como estan). Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plantas_lod3.json"
res = {"tocados": [], "err": []}
DIANA = ["boxwood", "bigleaf_hydrangea"]
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_class().get_name()!="StaticMeshActor": continue
    try:
        smc=a.get_component_by_class(unreal.StaticMeshComponent)
        if not smc: continue
        m=smc.get_editor_property("static_mesh")
        if not m: continue
        nm=m.get_name().lower()
        if any(k in nm for k in DIANA):
            nl=m.get_num_lods()
            if nl>=4:
                smc.set_editor_property("min_lod", 3)
                res["tocados"].append(a.get_actor_label())
    except Exception as e:
        res["err"].append(str(e)[:40])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("PLANTAS LOD3 %d" % len(res["tocados"]))
