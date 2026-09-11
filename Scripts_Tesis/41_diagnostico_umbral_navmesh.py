# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Prueba rutas exterior->interior y perfila la altura del navmesh en las entradas (detecta escalones que cortan).
# Por que se necesito: El pawn se frena en la entrada de Hacienda y Convento (posible desconexion por escalon).
# Resultado obtenido: (ver salida)
import unreal, json, traceback
out={'err':None}
try:
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); world=ues.get_editor_world()
    ns=unreal.NavigationSystemV1
    def path(s,e):
        try:
            p=ns.find_path_to_location_synchronously(world, unreal.Vector(*s), unreal.Vector(*e))
            if not p: return [False,0]
            try: return [bool(p.is_valid()), len(p.path_points)]
            except:
                pts=p.get_editor_property('path_points'); return [len(pts)>1,len(pts)]
        except Exception as e2: return ['ERR',str(e2)[:50]]
    out['path_hac_ext_int']=path((-7000,-3450,40),(-7000,-1500,60))
    out['path_hac_approach']=path((-7000,-3450,40),(-6700,-1300,90))
    out['path_conv_ext_int']=path((6300,2950,150),(6300,4600,200))
    def zprofile(x, y0, y1, step, z0):
        prof=[]
        y=y0
        while y<=y1:
            try:
                r=ns.project_point_to_navigation(world, unreal.Vector(x,y,z0), None, None, unreal.Vector(60,60,400))
                if r and not (abs(r.x)<1 and abs(r.y)<1): prof.append([y,round(r.z)])
                else: prof.append([y,'NONE'])
            except: prof.append([y,'ERR'])
            y+=step
        return prof
    out['hac_entry_Zprofile']=zprofile(-7000,-3400,-1500,120,200)
    out['conv_entry_Zprofile']=zprofile(6300,2900,4600,150,300)
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_umbral.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_umbral.json','w').write(json.dumps(out,indent=1))
