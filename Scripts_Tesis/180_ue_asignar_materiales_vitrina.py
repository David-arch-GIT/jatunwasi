# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Asigna a VIT_Habito_Vitrina los 5 materiales exactos que usan las vitrinas del folklore (slot0=vidrio
#   transparente M_HFS_glass, slot1=glow, slots2-4=madera). Asi el vidrio deja ver el habito. Elimina VIT_Habito_Glow
#   (redundante: la vitrina ya trae su glow en el slot1). Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/asignar_mats.json"
res = {"ok": [], "err": []}
eas = unreal.EditorActorSubsystem()
MATS = [
    "/Game/JWN/Props/Folklore/Mats/M_HFS_glass",
    "/Game/JWN/Props/Folklore/Mats/M_HFS_glow",
    "/Game/JWN/Props/Folklore/Mats/M_HFS_02",
    "/Game/JWN/Props/Folklore/Mats/M_HFS_03",
    "/Game/JWN/Props/Folklore/Mats/M_HFS_04",
]
loaded = [unreal.EditorAssetLibrary.load_asset(p) for p in MATS]
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab == "VIT_Habito_Vitrina":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            for i, mat in enumerate(loaded):
                if mat:
                    try:
                        c.set_material(i, mat)
                        res["ok"].append("slot%d=%s" % (i, MATS[i].split("/")[-1]))
                    except Exception as e:
                        res["err"].append("slot%d:%s" % (i, str(e)[:30]))
    if lab == "VIT_Habito_Glow":
        try:
            eas.destroy_actor(a)
            res["ok"].append("glow cube eliminado")
        except Exception as e:
            res["err"].append("del glow:" + str(e)[:30])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ASIGNAR MATS ok=%d" % len(res["ok"]))
