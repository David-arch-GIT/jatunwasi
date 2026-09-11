# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Corrige COL_Rampa_Entrada: rota con PITCH explicito (no roll) para que suba del terreno (z-5) al piso
#   (z59) de la hacienda en la entrada. Verifica el perfil con trazos (debe subir gradual). Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rampa_fix.json"
res = {"rot": None, "verif": [], "err": []}
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
# borrar rampa previa
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COL_Rampa_Entrada":
        eas.destroy_actor(a)
# recrear con pitch explicito
a = unreal.EditorLevelLibrary.spawn_actor_from_object(CUBE, unreal.Vector(-7085,-620,19))
a.set_actor_label("COL_Rampa_Entrada")
a.set_actor_scale3d(unreal.Vector(1.7,3.0,0.4))  # 170 x 300 x 40
r = unreal.Rotator(); r.pitch = -24.0; r.yaw = 0.0; r.roll = 0.0
a.set_actor_rotation(r, False)
res["rot"] = [r.pitch, r.yaw, r.roll]
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
smc.set_collision_profile_name("BlockAll")
a.set_actor_hidden_in_game(True)
try: smc.set_editor_property("cast_shadow", False)
except Exception: pass
# verificar perfil
def fz(x,y):
    rr=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,300),unreal.Vector(x,y,-120),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True,unreal.LinearColor(1,0,0),unreal.LinearColor(0,1,0),0.0)
    if rr is None: return "_"
    t=rr.to_tuple()
    if not t[0]: return "_"
    return "%d|%s"%(round(t[5].z),(t[9].get_actor_label()[:14] if t[9] else "?"))
x=-6980
while x>=-7320:
    res["verif"].append([x, fz(x,-620)]); x-=20
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
try: unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
except Exception as e: res["err"].append("save:"+str(e)[:60])
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("RAMPA FIX ok")
