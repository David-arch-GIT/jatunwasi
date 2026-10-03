import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/islas_nav.json"
res = {"borrados": [], "islas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
# 1) borrar navmesh grandes que permiten vagar (solo las usan las criaturas)
BORRAR = ["CONV_NavBounds", "ConvUpper_nav_added", "HAC_NavBounds"]
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label() in BORRAR:
        try: eas.destroy_actor(a); res["borrados"].append(a.get_actor_label())
        except Exception as e: res["err"].append("del:"+str(e)[:30])
# 2) islas pequeñas por criatura (centro, scale)  -> cubo base 100
ISLAS = {
    "Nav_Cria_Karisiri": ((5890.0, 4810.0, 100.0), (8.0, 8.0, 5.0)),    # 800x800, ~±400
    "Nav_Cria_Condenado": ((6510.0, 5390.0, 100.0), (8.0, 8.0, 5.0)),
    "Nav_Cria_Duende": ((-8150.0, -1750.0, 150.0), (11.0, 11.0, 7.0)),  # 1100x1100 ~±550
}
found = set()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in ISLAS:
        (cx, cy, cz), (sx, sy, sz) = ISLAS[lab]
        a.set_actor_location(unreal.Vector(cx, cy, cz), False, True)
        a.set_actor_scale3d(unreal.Vector(sx, sy, sz))
        res["islas"].append(lab + " ok")
        found.add(lab)
# crear islas faltantes
for lab, ((cx, cy, cz), (sx, sy, sz)) in ISLAS.items():
    if lab in found: continue
    try:
        v = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(cx, cy, cz))
        v.set_actor_label(lab); v.set_actor_scale3d(unreal.Vector(sx, sy, sz))
        res["islas"].append(lab + " creada")
    except Exception as e:
        res["err"].append("crear "+lab+":"+str(e)[:30])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
open(OUT, "w").write(json.dumps(res, indent=1))
