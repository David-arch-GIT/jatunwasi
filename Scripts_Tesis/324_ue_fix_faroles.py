# Unifica los 31 SM_JW_WallLantern al material BUENO de la plaza: hierro negro + vidrio ambar calido.
# NO toca los faroles de plaza/tradicionales (ya buenos). Unlit = sin costo de rendimiento.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_faroles.json"
res={"arreglados":0, "componentes":[], "err":[]}
EAL=unreal.EditorAssetLibrary
iron=EAL.load_asset("/Game/JWN/NwiroGenerated/PlazaTarata/V08_BlenderFinal/Meshes/M_PLZT_Iron_Black")
glass=EAL.load_asset("/Game/JWN/Lighting/M_Emis_FarolCalido")
if not iron or not glass:
    res["err"].append("no cargaron materiales: iron=%s glass=%s"%(bool(iron),bool(glass)))
else:
    eas=unreal.EditorActorSubsystem()
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            sm=c.get_editor_property("static_mesh")
            if not sm or sm.get_name()!="SM_JW_WallLantern": continue
            try:
                c.set_material(0, iron)   # slot M_Iron
                c.set_material(1, glass)  # slot M_Glass -> ambar calido
                # verificar que quedo
                ov=c.get_editor_property("override_materials")
                ok = len(ov)>=2 and ov[0] and ov[1] and ov[0].get_name()=="M_PLZT_Iron_Black" and ov[1].get_name()=="M_Emis_FarolCalido"
                if ok:
                    res["arreglados"]+=1
                else:
                    res["err"].append("verif fallo: "+str([m.get_name() if m else None for m in ov]))
                if len(res["componentes"])<5:
                    res["componentes"].append(a.get_actor_label()[:35])
            except Exception as e:
                res["err"].append(str(e)[:70])
open(OUT,"w").write(json.dumps(res,indent=1))
