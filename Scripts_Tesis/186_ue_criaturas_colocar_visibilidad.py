# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Bloque1: coloca las 3 criaturas con rig en su zona y oculta las estaticas.
#   - AppSK_Conv_Karisiri -> zona convento (5890,4810) suelo
#   - AppSK_Conv_Condenado -> zona convento (6510,5390) suelo
#   - AppSK_Hac_Duende -> se queda en el camino (-4021,807), solo baja a suelo
#   - Oculta App_Conv_Karisiri, App_Conv_Condenado, App_Hac_Duende (estaticas)
#   Reporta el centro de zona de cada criatura (para los radios despues). Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/criaturas_coloc.json"
res = {"movidas": [], "ocultadas": [], "zona_centros": {}, "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
def suelo(x, y, z0=300):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,z0), unreal.Vector(x,y,-300), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]: return float(t[5].z)
    return 0.0
DEST = {
    "AppSK_Conv_Karisiri": (5890.0, 4810.0),
    "AppSK_Conv_Condenado": (6510.0, 5390.0),
}
OCULTAR = ["App_Conv_Karisiri", "App_Conv_Condenado", "App_Hac_Duende"]
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab in DEST:
        x, y = DEST[lab]
        z = suelo(x, y)
        a.set_actor_location(unreal.Vector(x, y, z), False, True)
        res["movidas"].append([lab, round(x), round(y), round(z)])
        res["zona_centros"][lab] = [round(x), round(y), round(z)]
    elif lab == "AppSK_Hac_Duende":
        loc = a.get_actor_location()
        z = suelo(loc.x, loc.y)
        a.set_actor_location(unreal.Vector(loc.x, loc.y, z), False, True)
        res["zona_centros"][lab] = [round(loc.x), round(loc.y), round(z)]
        res["movidas"].append([lab, round(loc.x), round(loc.y), round(z), "(se queda en camino)"])
    if lab in OCULTAR:
        try:
            a.set_actor_hidden_in_game(True)
            a.set_is_temporarily_hidden_in_editor(True)
            res["ocultadas"].append(lab)
        except Exception as e:
            res["err"].append(lab + ":" + str(e)[:30])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("COLOC criaturas movidas=%d ocultadas=%d" % (len(res["movidas"]), len(res["ocultadas"])))
