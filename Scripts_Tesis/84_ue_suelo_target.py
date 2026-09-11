# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Ajusta cada AppSK_* para que la BASE de su bounding box quede en el suelo objetivo por zona (valores validados ~10-20). Reporta.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/suelo_target.json"
TARGET = {"AppSK_Conv_Karisiri": 15.0, "AppSK_Conv_Condenado": 18.0,
          "AppSK_Hac_Duende": 10.0, "AppSK_Plz_Duende": 10.0}
res = {"actors": []}
eas = unreal.EditorActorSubsystem()
by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for label, tgt in TARGET.items():
    a = by_label.get(label)
    if a is None:
        res["actors"].append({"label": label, "err": "no existe"}); continue
    loc = a.get_actor_location()
    b = a.get_actor_bounds(False)
    bottom = b[0].z - b[1].z
    delta = tgt - bottom
    a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + delta), False, True)
    res["actors"].append({"label": label, "bottom_antes": round(bottom, 1),
                          "z_antes": round(loc.z, 1), "z_despues": round(loc.z + delta, 1)})
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("SUELO TARGET done")
