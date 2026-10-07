# 370_ue_templo_draw_distance.py
# Proyecto: JatunWasiNawpakay (VR Quest 2)
# Objetivo: Arreglar "el templo no carga de lejos" (da impresion de error).
#   Causa: el casco (HISM TMP_ISM_01 muros, TMP_ISM_03 bloques) culling a 3500 (35m)
#   -> los muros desaparecen a 35m y queda solo la cupula flotando.
# Fix: subir distancia de culling a 30000 (300m) en instancias del casco + piezas
#   grandes (cupula/tambor/portal/WallE de 9000 -> 30000).
#   Seguro para Quest: son instancias (pocos draw calls) y mallas grandes/lejanas.
# Reversible: valores previos guardados en el JSON de salida.
import unreal, json, traceback
res={"ism":[],"smc":[],"err":None}
try:
    eas=unreal.EditorActorSubsystem()
    END=30000.0
    # 1) Todas las instancias del casco del templo (TMP_ISM_*) con culling corto
    for a in eas.get_all_level_actors():
        lbl=a.get_actor_label()
        if not lbl.startswith("TMP_ISM"): continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                s=c.get_editor_property("instance_start_cull_distance")
                e=c.get_editor_property("instance_end_cull_distance")
            except: continue
            # solo tocar los que SI tienen culling corto (>0 y < END); 0 = nunca culling, dejar
            if 0 < e < END:
                c.set_editor_property("instance_start_cull_distance", 0)
                c.set_editor_property("instance_end_cull_distance", int(END))
                res["ism"].append({"lbl":lbl,"antes":[round(s),round(e)],"ahora":[0,int(END)],"inst":c.get_instance_count()})
    # 2) Piezas grandes sueltas con ld_max 9000
    targets=("TMP_Dome","TMP_Drum","TMP_Portal","TMP_WallE_-1700")
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in targets:
            c=a.get_component_by_class(unreal.StaticMeshComponent)
            if c:
                old=c.get_editor_property("ld_max_draw_distance")
                if 0 < old < END:
                    c.set_editor_property("ld_max_draw_distance", END)
                    res["smc"].append({"lbl":a.get_actor_label(),"antes":round(old),"ahora":int(END)})
    res["ism_count"]=len(res["ism"]); res["smc_count"]=len(res["smc"])
except Exception as e:
    res["err"]=traceback.format_exc()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/draw_dist.json","w",encoding="utf-8").write(json.dumps(res,indent=1,default=str))
