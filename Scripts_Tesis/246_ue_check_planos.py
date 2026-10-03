import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/check_planos.json"
res = {}
eas = unreal.EditorActorSubsystem()
MEL = unreal.MaterialEditingLibrary
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if l in ["FotoPlano_MUS_Cuadro_03","FotoPlano_MUS_Cuadro_coc1","FotoPlano_MUS_Cuadro_00","FotoPlano_BALL_Cuadro_1"]:
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        m = smc.get_material(0)
        d = {"mat": m.get_name() if m else None}
        if isinstance(m, unreal.MaterialInstanceConstant):
            t = MEL.get_material_instance_texture_parameter_value(m, "Foto")
            d["foto"] = t.get_name() if t else None
            par = m.get_editor_property("parent")
            d["parent"] = par.get_name() if par else None
        sc = a.get_actor_scale3d()
        d["scale"] = [round(sc.x,2),round(sc.y,2),round(sc.z,2)]
        res[l] = d
open(OUT,"w").write(json.dumps(res,indent=1))
