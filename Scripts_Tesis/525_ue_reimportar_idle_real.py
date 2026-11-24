# 525_ue_reimportar_idle_real.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: reimportar en su MISMO lugar (como el script 80) los 3 *_full.glb rehechos por 524, cuyo
#   AnimSequence Idle es ahora el REPOSO real (antes era copia de la caminata: el duende "caminaba quieto").
#   Respaldo previo de Content/JWN/Apariciones/Anim. Verifica: Idle != Walk (rotacion de thigh_L), y que
#   las 3 Cria_* conservan malla, materiales de disolucion, IdleAnim/WalkAnim y desplazamiento de la malla.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reimport_525.json"
BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
res = {"err": None}
try:
    antes = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name() == "BP_CriaturaViva_C":
            m = a.get_component_by_class(unreal.SkeletalMeshComponent)
            antes[a.get_actor_label()] = [m.get_editor_property("skeletal_mesh_asset").get_path_name(), [x.get_name() if x else None for x in m.get_materials()], str(m.get_editor_property("relative_location"))]
    res["antes"] = antes
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    for name in ["duende", "condenado", "karisiri"]:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", BASE + name + "_full.glb")
        t.set_editor_property("destination_path", "/Game/JWN/Apariciones/Anim/%s" % name.capitalize())
        t.set_editor_property("automated", True); t.set_editor_property("save", True); t.set_editor_property("replace_existing", True)
        tools.import_asset_tasks([t])
        res["import_" + name] = [str(p) for p in t.get_editor_property("imported_object_paths")]
    def q(a, b, tt):
        r = unreal.AnimationLibrary.get_bone_pose_for_time(a, b, tt, False).rotation; return (r.x, r.y, r.z, r.w)
    def ang(q1, q2): return math.degrees(2 * math.acos(min(1.0, abs(sum(x * y for x, y in zip(q1, q2))))))
    B = "/Game/JWN/Apariciones/Anim/"
    for k, pre in (("duende", "Duende/duende_full/SkeletalMeshes/duende_fullduende_"), ("condenado", "Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_"), ("karisiri", "Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_")):
        ai = unreal.load_asset(B + pre + "Idle"); aw = unreal.load_asset(B + pre + "Walk")
        d = {"idle": bool(ai), "walk": bool(aw)}
        if ai and aw:
            d["len"] = [round(ai.get_play_length(), 2), round(aw.get_play_length(), 2)]
            for bone in ("thigh_L", "spine", "head", "upperarm_L"):
                try:
                    li = [q(ai, bone, ai.get_play_length() * i / 12) for i in range(13)]; lw = [q(aw, bone, aw.get_play_length() * i / 12) for i in range(13)]
                    d[bone] = [round(max(ang(li[0], x) for x in li), 1), round(max(ang(lw[0], x) for x in lw), 1)]
                except Exception as e:
                    d[bone] = str(e)[:60]
        res["cmp_" + k] = d
    despues = {}
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name() == "BP_CriaturaViva_C":
            m = a.get_component_by_class(unreal.SkeletalMeshComponent)
            despues[a.get_actor_label()] = [m.get_editor_property("skeletal_mesh_asset").get_path_name() if m.get_editor_property("skeletal_mesh_asset") else None, [x.get_name() if x else None for x in m.get_materials()], str(m.get_editor_property("relative_location")),
                                            a.get_editor_property("IdleAnim").get_name() if a.get_editor_property("IdleAnim") else None, a.get_editor_property("WalkAnim").get_name() if a.get_editor_property("WalkAnim") else None]
    res["despues"] = despues
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
