# 369_ue_templo_cerrar_abside.py
# Proyecto: JatunWasiNawpakay (VR Quest 2)
# Objetivo: Cerrar el abside del Templo detras de la Virgen de Urkupina.
#   Problema: faltan muro trasero y muro derecho; el muro izquierdo tiene puerta.
#   Se cuela el bosque/cielo nocturno detras del retablo.
# Solucion: muros solidos del mismo kit (SM_HACKIT_Wall_Solid) con material
#   MI_JW_TemploStone, escala uniforme-Z 1.6 como el muro existente (WallE).
#   NO cubos (regla AGENTS.md). Sombras off (regla Quest).
# Reversible: todos etiquetados TMP_ApseSeal_*.
import unreal, json, traceback
res={"placed":[],"err":None}
try:
    EAL=unreal.EditorAssetLibrary
    eas=unreal.EditorActorSubsystem()
    WALL="/Game/JWN/Architecture/Hacienda_Kit_V1/SM_HACKIT_Wall_Solid"
    MAT="/Game/JWN/Architecture/Hacienda_Kit_V1/MI_JW_TemploStone"
    mesh=EAL.load_asset(WALL); mat=EAL.load_asset(MAT)
    # limpiar intentos previos
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("TMP_ApseSeal_"):
            eas.destroy_actor(a)
    SCALE=unreal.Vector(1.0,1.0,1.6)
    def place(x,y,yaw,lbl):
        act=eas.spawn_actor_from_object(mesh, unreal.Vector(x,y,0.0))
        r=unreal.Rotator(); r.yaw=yaw; act.set_actor_rotation(r,False)
        act.set_actor_scale3d(SCALE)
        act.set_actor_label(lbl)
        smc=act.get_component_by_class(unreal.StaticMeshComponent)
        try:
            for i in range(smc.get_num_materials()): smc.set_material(i, mat)
        except: pass
        try: smc.set_editor_property("cast_shadow", False)
        except: pass
        o,ext=act.get_actor_bounds(False)
        res["placed"].append({"lbl":lbl,"xmin":round(o.x-ext.x),"xmax":round(o.x+ext.x),
            "ymin":round(o.y-ext.y),"ymax":round(o.y+ext.y),"zmin":round(o.z-ext.z),"zmax":round(o.z+ext.z)})
        return act
    # MURO TRASERO (yaw 0, ancho en X) en Y=14360, 3 piezas -> cubre X -600..600
    place(-400,14360,0.0,"TMP_ApseSeal_Back_L")
    place(   0,14360,0.0,"TMP_ApseSeal_Back_C")
    place( 400,14360,0.0,"TMP_ApseSeal_Back_R")
    # MURO DERECHO (yaw 90, largo en Y) en X=+555
    place( 555,14160,90.0,"TMP_ApseSeal_Right")
    # BLOQUEADOR IZQUIERDO detras del muro-puerta existente (yaw 90) en X=-600
    place(-600,14160,90.0,"TMP_ApseSeal_LeftDoorBlock")
    res["count"]=len(res["placed"])
except Exception as e:
    res["err"]=traceback.format_exc()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/apse_seal.json","w",encoding="utf-8").write(json.dumps(res,indent=1,default=str))
