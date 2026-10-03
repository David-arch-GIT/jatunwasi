# Activa colision de cartelas BP (para que el rayo las detecte) + cuenta BP vs StaticMeshActor.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/prep_cartelas.json"
res={"bp_cartela":[], "static_cartela":[], "colision_activada":0}
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    lbl=a.get_actor_label()
    es_cart = ("Cartela" in cn) or ("Cartela" in lbl) or ("cartela" in lbl.lower())
    if not es_cart: continue
    if "BP_Cartela" in cn:
        res["bp_cartela"].append(lbl[:30])
        # activar colision de TODOS sus componentes de colision/mesh para que el rayo pegue
        for c in a.get_components_by_class(unreal.PrimitiveComponent):
            try:
                c.set_editor_property("collision_enabled", unreal.CollisionEnabled.QUERY_ONLY)
                c.set_collision_profile_name("BlockAll")
                res["colision_activada"]+=1
            except Exception: pass
    else:
        res["static_cartela"].append(lbl[:30])
res["n_bp"]=len(res["bp_cartela"]); res["n_static"]=len(res["static_cartela"])
unreal.EditorLoadingAndSavingUtils.save_current_level()
res["guardado"]=True
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
