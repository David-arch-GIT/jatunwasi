# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Coloca 2 colisiones invisibles: (A) PUENTE escalera->corredor 2do piso (llena el vacio y-2250) y
#   (B) RAMPA entrada camino->piso hacienda (sube el escalon de ~64cm en x-7150, y-600). Ambas hidden-in-game + colision.
#   Luego VERIFICA con trazos que el perfil quedo continuo. Guarda robusto (level + assets).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/puentes.json"
res = {"spawn": [], "verif_cruce": [], "verif_entrada": [], "err": []}
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()

def make(name, loc, rot, scale):
    try:
        a = unreal.EditorLevelLibrary.spawn_actor_from_object(CUBE, unreal.Vector(*loc), unreal.Rotator(*rot))
        a.set_actor_label(name)
        a.set_actor_scale3d(unreal.Vector(*scale))
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        smc.set_collision_profile_name("BlockAll")
        a.set_actor_hidden_in_game(True)
        try: smc.set_editor_property("cast_shadow", False)
        except Exception: pass
        res["spawn"].append(name)
        return a
    except Exception as e:
        res["err"].append(name+":"+str(e)[:80]); return None

# limpiar previos si re-ejecuto
for a in eas.get_all_level_actors():
    if a.get_actor_label() in ("COL_Puente_Escalera2P","COL_Rampa_Entrada"):
        eas.destroy_actor(a)

# (A) PUENTE escalera->corredor: cubo 100. escala x2.0 y2.2 z0.4 => 200x220x40, top en z441
make("COL_Puente_Escalera2P", (-7590,-2300,421), (0,0,0), (2.0,2.2,0.4))
# (B) RAMPA entrada: cubo 100. escala x2.2 y2.8 z0.6 => 220x280x60, rotada pitch 18.6 grados, centro (x-7160,y-600,z30)
make("COL_Rampa_Entrada", (-7160,-600,30), (18.6,0,0), (2.2,2.8,0.6))

# VERIFICAR con trazos
def fz(x,y,zt=540,zb=-200):
    r=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,zt),unreal.Vector(x,y,zb),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True,unreal.LinearColor(1,0,0),unreal.LinearColor(0,1,0),0.0)
    if r is None: return "_"
    t=r.to_tuple()
    if not t[0]: return "_"
    return "%d|%s"%(round(t[5].z), (t[9].get_actor_label()[:16] if t[9] else "?"))
# cruce 2do piso
y=-2400
while y<=-2150:
    res["verif_cruce"].append([y, fz(-7588,y,540,380)]); y+=25
# entrada (moviendose -x hacia el piso)
x=-7000
while x>=-7300:
    res["verif_entrada"].append([x, fz(x,-600,300,-100)]); x-=25

# GUARDAR robusto
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
try: unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
except Exception as e: res["err"].append("save:"+str(e)[:60])
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("PUENTES ok")
