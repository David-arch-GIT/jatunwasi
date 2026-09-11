# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Lista TODOS los actores relacionados a apariciones (App*, Aparicion*, y skeletal/static con nombres de leyendas), con posicion, clase, hidden_ed y hidden_in_game. Para detectar duplicados/superpuestos flotando.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/investigar_app.json"
res = {"actores": []}
KW = ["app", "aparici", "karisiri", "duende", "condenado", "carreta"]
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    ll = l.lower()
    if any(k in ll for k in KW):
        loc = a.get_actor_location()
        try: hig = a.get_actor_hidden_in_game()
        except Exception: hig = "?"
        try: hed = a.is_hidden_ed()
        except Exception: hed = "?"
        res["actores"].append({
            "label": l, "cls": a.get_class().get_name(),
            "loc": [round(loc.x), round(loc.y), round(loc.z)],
            "hidden_ed": hed, "hidden_game": hig})
res["actores"].sort(key=lambda d: (d["loc"][0], d["loc"][1]))
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("INVESTIGAR done: %d" % len(res["actores"]))
