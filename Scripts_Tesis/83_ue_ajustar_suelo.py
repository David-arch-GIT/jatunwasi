# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Para cada AppSK_*, hace line trace al suelo y reubica el actor para que la BASE de su bounding box quede en el suelo. Robusto en el acceso al HitResult.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ajustar_suelo.json"
res = {"actors": []}
LABELS = ["AppSK_Conv_Karisiri", "AppSK_Conv_Condenado", "AppSK_Hac_Duende", "AppSK_Plz_Duende"]
eas = unreal.EditorActorSubsystem()
by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
world = unreal.EditorLevelLibrary.get_editor_world()

def hit_z(x, y):
    start = unreal.Vector(x, y, 5000); end = unreal.Vector(x, y, -2000)
    r = unreal.SystemLibrary.line_trace_single(world, start, end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
    hit = r[1] if isinstance(r, tuple) else r
    if hit is None: return None
    try:
        blk = hit.get_editor_property("blocking_hit")
        if not blk: return None
        return float(hit.get_editor_property("impact_point").z)
    except Exception:
        try: return float(hit.get_editor_property("location").z)
        except Exception: return None

for label in LABELS:
    a = by_label.get(label)
    if a is None:
        res["actors"].append({"label": label, "err": "no existe"}); continue
    loc = a.get_actor_location()
    gz = hit_z(loc.x, loc.y)
    info = {"label": label, "gz": (round(gz, 1) if gz is not None else None), "z_antes": round(loc.z, 1)}
    if gz is not None:
        b = a.get_actor_bounds(False)  # (origin, extent) world
        bottom = b[0].z - b[1].z
        delta = gz - bottom
        a.set_actor_location(unreal.Vector(loc.x, loc.y, loc.z + delta), False, True)
        info["z_despues"] = round(loc.z + delta, 1)
    res["actors"].append(info)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("AJUSTAR SUELO done")
