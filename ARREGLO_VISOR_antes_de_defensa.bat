@echo off
REM ============================================================
REM  ARREGLOS DEL VISOR - Ejecutar con el Quest por USB ANTES de la defensa
REM  (Se pierden al reiniciar el visor; por eso se reaplican con este .bat)
REM ============================================================
set ADB="C:\Users\Mi PC\AppData\Local\Android\Sdk\platform-tools\adb.exe"
echo Aplicando arreglos...
REM 1) Anti-cuelgue al quitarse el visor (sensor de proximidad)
%ADB% shell am broadcast -a com.oculus.vrpowermanager.prox_close --ei duration 86400000
%ADB% shell am broadcast -a com.oculus.vrpowermanager.prox_close
REM 2) Baja la carga de transmision/casting (menos resolucion/fps al transmitir)
%ADB% shell setprop debug.oculus.capture.width 1024
%ADB% shell setprop debug.oculus.capture.height 512
%ADB% shell setprop debug.oculus.capture.bitrate 3000000
%ADB% shell setprop debug.oculus.capture.fps 24
echo.
echo LISTO. Ya puedes desconectar el cable. Repite esto si reinicias el visor.
pause
