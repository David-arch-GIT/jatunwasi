# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Coloca la camara del visor en el centro de la plaza mirando al horizonte y captura, para verificar
#   visualmente que el bosque lejano tapa el vacio y no se ve plano. Tambien verifica altura de escalones de la hacienda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_plaza.json"
res = {"cam": None, "escalera_bounds": None, "err": []}
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
# camara en centro plaza mirando al horizonte (nivel de ojos ~170cm)
les.set_level_viewport_camera_info(unreal.Vector(0, -1000, 170), unreal.Rotator(0.0, 0.0, 0.0))
res["cam"] = "plaza centro (0,-1000,170) mirando +X horizonte"
# medir bounds de la escalera para estimar altura de escalones
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "HACV7_EXP_Staircase":
        o, e = a.get_actor_bounds(False)
        res["escalera_bounds"] = {"centro": [round(o.x),round(o.y),round(o.z)], "extent": [round(e.x),round(e.y),round(e.z)],
                                  "alto_total_cm": round(e.z*2)}
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("VERIF %s" % res)
