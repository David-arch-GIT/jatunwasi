# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Enumera TODAS las propiedades editables de una instancia BP_Apparition (via dir()+get_editor_property) para descubrir las variables del BP (textura, escala, malla, opacidad, sonido) que usa su Construction Script.
# Por que se necesito: El BP revierte los cambios directos al componente; hay que setear sus variables internas.
# Resultado obtenido: (pendiente) lista de variables del BP con su valor.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vars_bp.json"

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

# props estandar de AActor/objeto que queremos ignorar (ruido)
IGNORAR = set(dir(unreal.StaticMeshActor))

target = None
for a in all_actors():
    if a.get_actor_label() == "App_Conv_Karisiri":
        target = a
        break

res = {"encontrado": target is not None, "vars": {}}
if target:
    for n in dir(target):
        if n.startswith("_"):
            continue
        if n in IGNORAR:
            continue
        try:
            v = target.get_editor_property(n)
        except Exception:
            continue
        # ignorar callables
        if callable(v):
            continue
        s = str(v)
        if len(s) > 120:
            s = s[:120] + "..."
        res["vars"][n] = s

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("VARS BP: %d" % len(res["vars"]))
