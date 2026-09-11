# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Prueba si existe camino navegable (NavMesh) cruzando puertas de la Hacienda.
# Por que se necesito: Verificar que la reconstruccion del NavMesh permite pasar por los vanos.
# Resultado obtenido: (ver salida) - validez de rutas entre salas.
import unreal, json, traceback
out={'err':None,'paths':[]}
try:
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); world=ues.get_editor_world()
    tests=[
      ('patio->folklore',(-7000,-2400,60),(-6700,-1300,90)),
      ('folklore->este',(-6700,-1300,90),(-5600,-1900,60)),
      ('patio->salonbaja',(-7300,-2300,60),(-8100,-1500,60)),
      ('folklore_ancho',(-7400,-1300,90),(-5900,-900,60)),
    ]
    for nm,s,e in tests:
        try:
            path=unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(*s), unreal.Vector(*e))
            valid=False; pts=0
            if path:
                try: valid=path.is_valid(); pts=len(path.path_points)
                except:
                    try: valid=len(path.get_editor_property('path_points'))>1; pts=len(path.get_editor_property('path_points'))
                    except: pass
            out['paths'].append([nm,bool(valid),pts])
        except Exception as e2:
            out['paths'].append([nm,'ERR',str(e2)[:60]])
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_paso.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_paso.json','w').write(json.dumps(out,indent=1))
