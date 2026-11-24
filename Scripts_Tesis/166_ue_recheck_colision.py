# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: reverifica BIEN la colision de las barreras (perfil,
#   collision enabled, respuesta a Pawn) reportando errores (sin try/except silencioso).
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
R={"muestra":[], "resumen":{"bloquea":0,"no_bloquea":0,"sin_comp":0}}
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
targets=["COL_PathWall_CV_0_L","COL_PathWall_TM_0_L","COL_PathWall_HC_0_L",
         "COL_PlazaWall_N_W","COL_PlazaWall_E_S","HACV7_EXP_ExteriorWalls_Ground",
         "COL_ConvUpper_N","TMP_WallE_"]
def pawn_blocks(comp):
    prof=str(comp.get_collision_profile_name())
    ce=str(comp.get_collision_enabled())
    try:
        resp=str(comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN))
    except Exception as e:
        resp="ERR:"+str(e)[:50]
    blocks = ("BLOCK" in resp.upper()) or (prof in ("BlockAll","InvisibleWall","InvisibleWallDynamic","BlockAllDynamic"))
    return prof,ce,resp,blocks
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    if lbl in targets or lbl.startswith("COL_PathWall") or lbl.startswith("COL_PlazaWall"):
        comps=a.get_components_by_class(unreal.StaticMeshComponent)
        if not comps:
            comps=a.get_components_by_class(unreal.PrimitiveComponent)
        if not comps:
            R["resumen"]["sin_comp"]+=1
            if lbl in targets: R["muestra"].append({"lbl":lbl,"nota":"sin StaticMesh/Primitive comp"})
            continue
        prof,ce,resp,blocks=pawn_blocks(comps[0])
        if blocks: R["resumen"]["bloquea"]+=1
        else: R["resumen"]["no_bloquea"]+=1
        if lbl in targets or R["resumen"]["bloquea"]+R["resumen"]["no_bloquea"]<=6:
            R["muestra"].append({"lbl":lbl,"perfil":prof,"enabled":ce,"resp_pawn":resp,"bloquea":blocks})
open(out+"/recheck_colision.json","w").write(json.dumps(R,indent=1))
print("RECHECK_DONE", json.dumps(R["resumen"]))
