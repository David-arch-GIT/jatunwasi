import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/datos_obj.json"
res={"obj":{}}
eas=unreal.EditorActorSubsystem()
MAP={
 "varon_valluno":["HF_ManiquiM_G"],
 "pollera_cochabambina":["HF_ManiquiF_G"],
 "charango":["G_charango2"],
 "zampona":["G_zampona"],
 "quena":["SM_quena"],
 "tarka":["HF_Tarka","KitFolklore_SM_HF_Tarka"],
 "acordeon":["G_acordeon"],
 "catre":["CV2_Catre"],
 "habito":["VIT_Habito_Mesh","VIT_Habito_Vitrina"],
 "altar_convento":["CONV_Altar"],
 "urkupina":["Santo_Virgen_Urkupina"],
 "nino_sikimira":["Santo_Nino_Sikimira"],
 "san_sebastian":["Santo_San_Sebastian"],
 "cristo_llora":["Santo_Cristo_Llorando"],
 "santa_vera_cruz":["Santo_Santa_Vera_Cruz"],
 "retablo":["Retablo_Barroco_Mayor"],
 "altar_mayor":["Altar_Mayor_Exento"],
 "pulpito":["Pulpito"],
 "confesionario":["Confesionario_Nuevo_L"],
}
byl={}
for a in eas.get_all_level_actors():
    byl[a.get_actor_label()]=a
for cart,labels in MAP.items():
    found=None
    for lb in labels:
        if lb in byl: found=byl[lb]; break
    if not found:
        res["obj"][cart]={"err":"no actor"}; continue
    o,e=found.get_actor_bounds(False)
    rot=found.get_actor_rotation()
    res["obj"][cart]={"lbl":found.get_actor_label(),
        "o":[round(o.x,1),round(o.y,1),round(o.z,1)],
        "e":[round(e.x,1),round(e.y,1),round(e.z,1)],
        "yaw":round(rot.yaw,1)}
open(OUT,"w").write(json.dumps(res,indent=1))
