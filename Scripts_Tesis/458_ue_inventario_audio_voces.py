# 458_ue_inventario_audio_voces.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) inventario de TODAS las fuentes de audio para detectar choques de voces con
#   Convai: componentes de audio del nivel (actor, sonido, clase de sonido, concurrencia, auto-activar,
#   espacializado), componentes Convai (chatbot de Adela / player del pawn) y sus propiedades de audio,
#   y los SoundWave de voz (relatos, Adela, cartelas, apariciones): duracion, clase y concurrencia.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inventario_audio.json"
res = {"err": None, "comps": [], "convai": [], "waves": {}}
def nm(o):
    if not o: return None
    try: return o.get_name()
    except Exception: return str(o)[-60:]
def sv(o, k):
    try: return o.get_editor_property(k)
    except Exception: return "?"
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        for c in a.get_components_by_class(unreal.AudioComponent):
            cls = c.get_class().get_name()
            s = sv(c, "sound")
            conc = sv(c, "concurrency_set")
            d = {"actor": lb, "comp": c.get_name(), "cls": cls, "sound": nm(s) if s != "?" else "?",
                 "auto": sv(c, "auto_activate"), "spat": sv(c, "allow_spatialization"),
                 "vol": round(sv(c, "volume_multiplier"), 2) if isinstance(sv(c, "volume_multiplier"), float) else None,
                 "conc_comp": [nm(x) for x in conc] if isinstance(conc, (list, set, unreal.Set, unreal.Array)) else str(conc)[:60],
                 "sclass_comp": nm(sv(c, "sound_class_override")) if sv(c, "sound_class_override") not in ("?", None) else None}
            if "Convai" in cls:
                res["convai"].append(d)
            else:
                res["comps"].append(d)
        for c in a.get_components_by_class(unreal.ActorComponent):
            if "Convai" in c.get_class().get_name() and not isinstance(c, unreal.AudioComponent):
                res["convai"].append({"actor": lb, "comp": c.get_name(), "cls": c.get_class().get_name()})
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for path in ("/Game/JWN/Audio", "/Game/Cartelas/Audio"):
        for ad in ar.get_assets_by_path(path, True):
            if str(ad.asset_class_path.asset_name) != "SoundWave": continue
            w = ad.get_asset()
            conc = sv(w, "concurrency_set")
            res["waves"][str(ad.package_name)] = {"dur": round(w.get_editor_property("duration"), 1),
                "class": nm(sv(w, "sound_class_object")), "conc": [nm(x) for x in conc] if conc not in ("?", None) else None,
                "loop": sv(w, "looping"), "prio": round(sv(w, "priority"), 1) if isinstance(sv(w, "priority"), float) else None}
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=0, default=str))
