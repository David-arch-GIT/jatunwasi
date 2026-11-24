# 195_fix_culling.py
# Sube el cull de la ESTRUCTURA de edificios (muros/arcos/columnas/etc, instanciada=barata)
# para que no desaparezcan de lejos. NO toca el bosque PCG (perf). Foliage de zona a 90m.
import unreal, json, traceback
R={"estructura":0, "foliage":0, "skip":0, "err":[]}
STRUCT=["HACKIT","KitConvento","KitTemplo","Wall","Arch","Column","Balcony","Railing",
        "Door","Window","Stair","Roof","Beam","Cube","Plane","Arco","Muro","Columna"]
FOL=["Bush","Fern","Grass","Plant","ForestPlant","Helecho"]
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        lbl=a.get_actor_label()
        if lbl.startswith("PCG_"):  # NO tocar el bosque
            continue
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                if c.get_instance_count()==0: continue
                m=c.get_editor_property("static_mesh")
                mn=m.get_name() if m else ""
                end=c.get_editor_property("instance_end_cull_distance")
                is_fol=any(k.lower() in mn.lower() for k in FOL)
                is_struct=any(k.lower() in mn.lower() for k in STRUCT)
                if is_fol:
                    if end!=0 and end<9000:
                        c.set_editor_property("instance_start_cull_distance", 0)
                        c.set_editor_property("instance_end_cull_distance", 9000)
                        R["foliage"]+=1
                elif is_struct:
                    if end!=0 and end<15000:
                        c.set_editor_property("instance_start_cull_distance", 0)
                        c.set_editor_property("instance_end_cull_distance", 15000)
                        R["estructura"]+=1
                else:
                    R["skip"]+=1
            except Exception as e:
                R["err"].append(str(e)[:40])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cullfix.json","w").write(json.dumps(R))
