# 198_fix_flote_capsula.py
# Causa real del flote en RUNTIME: Character pega la base de la capsula al piso,
# pero la malla esta centrada -> flota ~media capsula. Fix: offset malla Z = -(half height).
import unreal, json, traceback
R={"fix":[], "err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende"]:
        a=None
        for x in eas.get_all_level_actors():
            if x.get_actor_label()==lbl: a=x; break
        if not a: R["err"].append("no_"+lbl); continue
        cap=a.get_component_by_class(unreal.CapsuleComponent)
        smc=a.get_component_by_class(unreal.SkeletalMeshComponent)
        hh=cap.get_scaled_capsule_half_height() if cap else 90.0
        rel=smc.get_editor_property("relative_location")
        newrel=unreal.Vector(rel.x, rel.y, -(hh))
        smc.set_editor_property("relative_location", newrel)
        # asegurar rotacion de malla tipica de Character (-90 yaw) solo si esta en 0
        rr=smc.get_editor_property("relative_rotation")
        R["fix"].append({"lbl":lbl,"half_h":round(hh),"mesh_relZ_antes":round(rel.z),
            "mesh_relZ_ahora":round(-hh),"mesh_yaw":round(rr.yaw)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flote_cap.json","w").write(json.dumps(R))
