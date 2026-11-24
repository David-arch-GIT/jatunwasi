# 475_ue_walk_en_sitio.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: A_Adela_walk desplaza la pelvis +159 u (x1.651 = 2.6 m) por ciclo de 2.33 s (no hay root
#   motion) -> si el actor se mueve por codigo, la malla "salta atras" al reiniciar el bucle.
#   Se crea A_Adela_walk_sitio (copia) quitando la deriva LINEAL de la pelvis en X/Y (se conserva el
#   balanceo y el sube-baja). No toca la original. Reporta la velocidad natural del paso (cm/s en mundo).
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/walk_sitio.json"
res = {"err": None}
try:
    D = "/Game/JWN/Characters/AdelaFinal"
    src = D + "/A_Adela_walk"; dst = D + "/A_Adela_walk_sitio"
    if not unreal.EditorAssetLibrary.does_asset_exist(dst):
        unreal.EditorAssetLibrary.duplicate_asset(src, dst)
    seq = unreal.load_asset(dst)
    n = unreal.AnimationLibrary.get_num_frames(seq) if hasattr(unreal.AnimationLibrary, "get_num_frames") else seq.get_editor_property("number_of_sampled_keys")
    res["frames"] = n
    poses = [unreal.AnimationLibrary.get_bone_pose_for_frame(seq, "pelvis", f, False) for f in range(n + 1)]
    p0 = poses[0].translation; pn = poses[-1].translation
    dx = (pn.x - p0.x) / n; dy = (pn.y - p0.y) / n
    res["deriva_por_ciclo"] = [round(pn.x - p0.x, 1), round(pn.y - p0.y, 1)]
    res["vel_natural_cm_s"] = round((pn.x - p0.x) * 1.651 / seq.get_play_length(), 1)
    pos = []; rot = []; scl = []
    for f, t in enumerate(poses):
        v = t.translation
        pos.append(unreal.Vector(v.x - dx * f, v.y - dy * f, v.z)); rot.append(t.rotation); scl.append(t.scale3d)
    ctrl = seq.get_editor_property("controller") if False else seq.controller
    ok = ctrl.set_bone_track_keys("pelvis", pos, rot, scl, True)
    res["set_ok"] = ok
    q0 = unreal.AnimationLibrary.get_bone_pose_for_frame(seq, "pelvis", 0, False).translation
    qn = unreal.AnimationLibrary.get_bone_pose_for_frame(seq, "pelvis", n, False).translation
    qm = unreal.AnimationLibrary.get_bone_pose_for_frame(seq, "pelvis", n // 2, False).translation
    res["despues"] = {"ini": [round(q0.x, 1), round(q0.y, 1), round(q0.z, 1)], "medio": [round(qm.x, 1), round(qm.y, 1), round(qm.z, 1)], "fin": [round(qn.x, 1), round(qn.y, 1), round(qn.z, 1)]}
    res["saved"] = unreal.EditorAssetLibrary.save_asset(dst, False)
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
