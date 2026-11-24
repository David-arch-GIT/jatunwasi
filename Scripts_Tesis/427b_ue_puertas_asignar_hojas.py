# 427b_ue_puertas_asignar_hojas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: corregir 427: al tocar un componente heredado del BP, Unreal re-ejecuta la construccion
#   del actor y las demas referencias quedan obsoletas; set_static_mesh() ademas no se registra como
#   cambio de instancia. Aqui: por cada cambio se vuelve a buscar el componente y se usa
#   set_editor_property (static_mesh / relative_location / collision) que SI persiste. Verifica al final.
import unreal, json, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/puertas_hojas.json"
DST = "/Game/JWN/Puertas/"
rep = json.load(open(ROOT + "/Saved/Models/puertas/report.json"))
T, H, C = rep["templo"], rep["hacienda"], rep["convento"]
YF = -1.0
CFG = {
    "PUERTA_Templo": ("SM_PuertaTemplo_HojaIzq", "SM_PuertaTemplo_HojaDer", T["hinge_x"], T["pivot_y"]),
    "PUERTA_Hacienda": ("SM_PuertaHacienda_HojaIzq", "SM_PuertaHacienda_HojaDer", H["hinge_x"], H["pivot_y"]),
    "PUERTA_Convento_A": (None, "SM_PuertaConvento_HojaDer", C["hinge_x"], C["pivot_y"]),
    "PUERTA_Convento_B": ("SM_PuertaConvento_HojaIzq", None, C["hinge_x"], C["pivot_y"]),
}
res = {"err": None}
def comp(actor, prefix):
    return [c for c in actor.get_components_by_class(unreal.StaticMeshComponent) if c.get_name().startswith(prefix)][0]
try:
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith("PUERTA_")}
    for lb, (ml, mr, hx, py) in CFG.items():
        a = acts[lb]
        for pre, mesh, sx in (("HojaIzq", ml, -1), ("HojaDer", mr, 1)):
            sm = unreal.load_asset(DST + mesh) if mesh else None
            comp(a, pre).set_editor_property("static_mesh", sm)
            comp(a, pre).set_editor_property("relative_location", unreal.Vector(sx * hx * 100.0, YF * py * 100.0, 0.0))
            if not mesh:
                comp(a, pre).set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        out = []
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            rl = c.get_editor_property("relative_location")
            out.append([c.get_name(), c.static_mesh.get_name() if c.static_mesh else None, [round(rl.x, 1), round(rl.y, 1)]])
        res[lb] = out
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
