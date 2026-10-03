# Mas reduccion SEGURA: distancia de dibujo a cartelas (overdraw translucido) + afinar pasto de suelo.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reducir_mas.json"
res={"cartelas_draw":0,"pasto_reducido":{"antes":0,"despues":0}}
eas=unreal.EditorActorSubsystem()
# 1) Cartelas: max_draw_distance 1300cm (13m) al panel (solo se leen de cerca)
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    lbl=a.get_actor_label()
    if "Cartela" in cn or "Cartela" in lbl or "Cart_" in lbl:
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                c.set_editor_property("max_draw_distance", 1300.0)
                res["cartelas_draw"]+=1
            except Exception: pass
# 2) Afinar SOLO pasto/musgo de suelo (ground cover puro) otro ~30%
GROUND=["GrassForest","Mossy_Grass"]
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        sm=c.get_editor_property("static_mesh")
        if not sm: continue
        mn=sm.get_name()
        if not any(k in mn for k in GROUND): continue
        try: n=c.get_instance_count()
        except Exception: n=0
        if n<20: continue
        res["pasto_reducido"]["antes"]+=n
        rem=[i for i in range(n) if i%10<3]  # ~30%
        try:
            c.remove_instances(rem)
            res["pasto_reducido"]["despues"]+=c.get_instance_count()
        except Exception:
            res["pasto_reducido"]["despues"]+=n
unreal.EditorLoadingAndSavingUtils.save_current_level()
res["guardado"]=True
open(OUT,"w").write(json.dumps(res,indent=1))
