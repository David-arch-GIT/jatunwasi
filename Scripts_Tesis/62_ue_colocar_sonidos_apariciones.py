# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Importa los 3 WAV de aparicion como SoundWave (loop), y coloca AmbientSound espacializados en cada App3D_* con atenuacion localizada. No toca nada mas del escenario.
# Por que se necesito: Sonido de miedo por leyenda (Karisiri/Condenado/Duende), audible solo cerca de cada aparicion.
# Resultado obtenido: (pendiente) AmbientSounds colocados y en bucle.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar_sonidos.json"
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/sonidos/"
DEST = "/Game/JWN/Audio/Apariciones"
res = {"import": [], "colocados": []}
tools = unreal.AssetToolsHelpers.get_asset_tools()

FILES = {"karisiri": "snd_karisiri.wav", "condenado": "snd_condenado.wav", "duende": "snd_duende.wav"}

# 1) Importar WAV -> SoundWave y poner looping
SW = {}
for k, fn in FILES.items():
    task = unreal.AssetImportTask()
    task.filename = SRC + fn
    task.destination_path = DEST
    task.automated = True
    task.replace_existing = True
    task.save = True
    tools.import_asset_tasks([task])
    p = DEST + "/" + fn.replace(".wav", "")
    sw = unreal.load_asset(p)
    if sw:
        try:
            sw.set_editor_property("looping", True)
        except Exception as e:
            res.setdefault("loop_err", []).append(str(e))
        unreal.EditorAssetLibrary.save_asset(p)
    SW[k] = sw
    res["import"].append({"snd": k, "ok": sw is not None})

# 2) Atenuacion localizada (reusar la de narracion si existe)
sa = unreal.load_asset("/Game/JWN/Audio/SA_JW_Narration")
res["atenuacion"] = "SA_JW_Narration" if sa else None

# 3) Mapear App3D_* -> sonido
MAP = {"Karisiri": "karisiri", "Condenado": "condenado", "Duende": "duende"}
VOL = {"karisiri": 0.85, "condenado": 0.85, "duende": 0.95}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

# limpiar AmbientSounds de aparicion previos (por si se re-ejecuta)
for a in list(all_actors()):
    if a.get_actor_label().startswith("Snd_App_"):
        unreal.EditorLevelLibrary.destroy_actor(a)

for a in all_actors():
    lab = a.get_actor_label()
    if not lab.startswith("App3D_"):
        continue
    key = None
    for tag, k in MAP.items():
        if tag.lower() in lab.lower():
            key = k
            break
    if key is None or SW.get(key) is None:
        continue
    loc = a.get_actor_location()
    amb = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.AmbientSound, unreal.Vector(loc.x, loc.y, loc.z + 60))
    amb.set_actor_label("Snd_App_" + lab.replace("App3D_", ""))
    ac = amb.get_editor_property("audio_component")
    ac.set_editor_property("sound", SW[key])
    ac.set_editor_property("volume_multiplier", VOL[key])
    if sa:
        ac.set_editor_property("attenuation_settings", sa)
    try:
        ac.set_editor_property("auto_activate", True)
    except Exception:
        pass
    res["colocados"].append({"actor": amb.get_actor_label(), "snd": key})

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("SONIDOS colocados: %d" % len(res["colocados"]))
