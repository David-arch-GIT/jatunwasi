# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Encuentra la escalera de la hacienda (posicion, bounds, colision) y el step height
#   del pawn VR, para decidir como hacerla subible (rampa invisible o step height).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/escaleras.json"
res = {"escaleras": [], "pawn_step_height": None, "gamemode": None, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label(); low = lbl.lower()
    if "stair" in low or "escalera" in low or "staircase" in low:
        try:
            loc = a.get_actor_location()
            org, ext = a.get_actor_bounds(False)
            info = {"label": lbl,
                    "loc": [round(loc.x), round(loc.y), round(loc.z)],
                    "bounds_origin": [round(org.x), round(org.y), round(org.z)],
                    "bounds_ext": [round(ext.x), round(ext.y), round(ext.z)]}
            # colision de sus componentes
            cols = []
            for comp in a.get_components_by_class(unreal.StaticMeshComponent):
                try:
                    ce = comp.get_collision_enabled()
                    cols.append(str(ce))
                except Exception:
                    pass
            info["collision"] = cols
            res["escaleras"].append(info)
        except Exception as e:
            res["err"].append("%s: %s" % (lbl, str(e)[:50]))
# step height del pawn (buscar CharacterMovement en pawns del nivel)
for a in eas.get_all_level_actors():
    cmc = a.get_component_by_class(unreal.CharacterMovementComponent)
    if cmc:
        try:
            res["pawn_step_height"] = {"actor": a.get_actor_label(), "max_step_height": float(cmc.get_editor_property("max_step_height"))}
        except Exception as e:
            res["err"].append("cmc: %s" % e)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ESCALERAS enc=%d step=%s" % (len(res["escaleras"]), res["pawn_step_height"]))
