# 489_ue_fix_concurrencia_voces.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG REAL (previo): SC_Narracion tenia enable_max_count_platform_scaling=True con
#   platform_max_count=16 -> el motor IGNORA max_count=1 y permite 16 voces a la vez (narraciones, cartelas
#   y Adela se superponian). Se desactiva el escalado por plataforma (max_count=1 efectivo) y se pone
#   tambien platform_max_count=1 por seguridad. Respaldo del .uasset. Guarda.
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_concurrencia.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/Audio/SC_Narracion.uasset", ROOT + "/Saved/ClaudeBackups/SC_Narracion_pre_fix.uasset")
    sc = unreal.load_asset("/Game/JWN/Audio/SC_Narracion")
    s = sc.get_editor_property("concurrency")
    try:
        pm = s.get_editor_property("platform_max_count"); pm.set_editor_property("default", 1); s.set_editor_property("platform_max_count", pm)
    except Exception as e:
        res["pm_err"] = str(e)[:120]
    s.set_editor_property("enable_max_count_platform_scaling", False)
    s.set_editor_property("max_count", 1)
    sc.set_editor_property("concurrency", s)
    res["guardado"] = unreal.EditorAssetLibrary.save_asset("/Game/JWN/Audio/SC_Narracion", False)
    s2 = unreal.load_asset("/Game/JWN/Audio/SC_Narracion").get_editor_property("concurrency")
    res["ahora"] = {k: str(s2.get_editor_property(k)) for k in ("max_count", "enable_max_count_platform_scaling", "resolution_rule")}
    try: res["ahora"]["platform_default"] = s2.get_editor_property("platform_max_count").get_editor_property("default")
    except Exception: pass
except Exception:
    res["err"] = traceback.format_exc()[:1000]
open(OUT, "w").write(json.dumps(res))
