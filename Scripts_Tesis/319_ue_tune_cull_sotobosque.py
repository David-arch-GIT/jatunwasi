# Ajuste conservador de cull SOLO en sotobosque (helechos/maleza/musgo) del bosque.
# Deja intactos: arboles, flores, pasto (ya 25m), boxwood, estructura (Cube/Plane/Wall).
# UE hace fade dither entre start y end -> transicion suave, sin pop. Unidades cm.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/tune_cull.json"
# mesh_name -> (start, end) nuevos, mas ajustados pero con banda de fade amplia
TARGET={
 "SM_Fern_01":         (2500,3500),
 "SM_ForestPlant_A_01":(2500,3500),
 "SM_Fern_02":         (3500,5000),
 "SM_ForestBush_01":   (4500,6000),
 "SM_ForestBush_02":   (4500,6000),
 "SM_Mossy_Grass_01":  (3500,5000),
 "SM_Mossy_Grass_02":  (3500,5000),
}
res={"cambiados":[], "comps":0, "inst":0}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m=c.get_editor_property("static_mesh")
        if not m: continue
        mn=m.get_name()
        if mn not in TARGET: continue
        try: n=c.get_instance_count()
        except Exception: n=0
        if n==0: continue
        s,e=TARGET[mn]
        old_s=c.get_editor_property("instance_start_cull_distance")
        old_e=c.get_editor_property("instance_end_cull_distance")
        # solo achicar, nunca agrandar
        if old_e>0 and old_e<=e: continue
        c.set_editor_property("instance_start_cull_distance", s)
        c.set_editor_property("instance_end_cull_distance", e)
        try: c.mark_render_state_dirty()
        except Exception: pass
        res["comps"]+=1; res["inst"]+=n
        res["cambiados"].append({"mesh":mn,"inst":n,"de":[old_s,old_e],"a":[s,e]})
open(OUT,"w").write(json.dumps(res,indent=1))
