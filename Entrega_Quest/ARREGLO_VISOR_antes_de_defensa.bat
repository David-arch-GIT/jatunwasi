@echo off
REM ============================================================
REM  ARREGLO DEL VISOR - Ejecutar con el Quest por USB ANTES de la defensa
REM  (Se pierde al reiniciar el visor; reaplicar con este .bat cada vez)
REM  IMPORTANTE: el Quest debe estar FRIO y CARGADO al 100% (caliente = se cuelga)
REM ============================================================
set ADB="C:\Users\Mi PC\AppData\Local\Android\Sdk\platform-tools\adb.exe"
echo.
echo === Aplicando MODO KIOSCO (anti-cuelgue robusto) ===
REM 0) CLAVE: pausar Guardian -> mata el ANR "DOFF_FROM_GUARDIAN took >15s" (la causa raiz confirmada en los logs)
%ADB% shell setprop debug.oculus.guardian_pause 1
REM 1) Sensor de proximidad "cerrado" -> no se duerme al quitarse el visor
%ADB% shell am broadcast -a com.oculus.vrpowermanager.prox_close
REM 2) Timeout de suspension a ~2h -> nunca se duerme por inactividad (esto es lo que faltaba)
%ADB% shell settings put system screen_off_timeout 7200000
echo.
echo === Bajando la carga de transmision/casting (menos GPU al transmitir) ===
%ADB% shell setprop debug.oculus.capture.width 1024
%ADB% shell setprop debug.oculus.capture.height 512
%ADB% shell setprop debug.oculus.capture.bitrate 2500000
%ADB% shell setprop debug.oculus.capture.fps 24
echo.
echo LISTO. Verifica que diga "Broadcast completed: result=0" arriba.
echo Ya puedes desconectar el cable.
echo.
echo RECORDATORIO PARA LA DEFENSA:
echo  - Visor FRIO y cargado al 100%%.
echo  - (Garantia 100%%) cinta opaca chica sobre el sensor de proximidad (entre las lentes).
echo  - Para que el jurado mire: usar el VIDEO grabado del recorrido, no transmitir en vivo.
pause
