# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Cambia Package Name, Orientation (Sensor Landscape) e Install Location (Auto) en AndroidRuntimeSettings.
# Por que se necesito: Meta rechazo el APK por package name invalido, orientacion no horizontal e install location no auto.
# Resultado obtenido: (ver salida) - ajustes escritos a DefaultEngine.ini.
import unreal, json, traceback
out={'err':None,'set':{}}
try:
    s=unreal.get_default_object(unreal.AndroidRuntimeSettings)
    # package name
    try:
        old=s.get_editor_property('package_name'); s.set_editor_property('package_name','com.jatunwasi.nawpaqay')
        out['set']['package_name']=[str(old),'com.jatunwasi.nawpaqay']
    except Exception as e: out['pkg_err']=str(e)[:100]
    # orientation
    try:
        old=s.get_editor_property('orientation'); s.set_editor_property('orientation',unreal.AndroidScreenOrientation.SENSOR_LANDSCAPE)
        out['set']['orientation']=[str(old),'SENSOR_LANDSCAPE']
    except Exception as e: out['orient_err']=str(e)[:100]
    # install location
    try:
        old=s.get_editor_property('install_location'); s.set_editor_property('install_location',unreal.AndroidInstallLocation.AUTO)
        out['set']['install_location']=[str(old),'AUTO']
    except Exception as e: out['inst_err']=str(e)[:100]
    # save to ini
    try:
        s.save_config(); out['saved']=True
    except Exception as e:
        try:
            unreal.SystemLibrary.save_config(s); out['saved']='via_systemlib'
        except Exception as e2: out['save_err']=str(e)[:60]+' | '+str(e2)[:60]
    # read back
    out['readback']={
      'package_name':str(s.get_editor_property('package_name')),
      'orientation':str(s.get_editor_property('orientation')),
      'install_location':str(s.get_editor_property('install_location')),
    }
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cfg_android.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cfg_android.json','w').write(json.dumps(out,indent=1))
