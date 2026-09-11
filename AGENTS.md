# Reglas de trabajo del proyecto

Estas reglas se aplican a todo el proyecto `JatunWasiNawpakay`.

## Seguridad del contenido

- No modificar ni borrar mapas sin crear antes una copia de trabajo.
- No borrar assets del Content Browser sin autorización explícita.
- Antes de cambiar un nivel, realizar un inventario y una captura del viewport.
- Guardar únicamente cuando la fase haya sido verificada.
- Conservar los logs y detenerse ante el primer error real.

## Construcción y arquitectura

- No utilizar cubos como arquitectura visible final.
- No aplicar escala no uniforme a elementos arquitectónicos.
- Mantener la escala VR: 1 Unreal Unit equivale a 1 centímetro.
- No continuar con otro edificio hasta validar el anterior.
- No colocar vegetación hasta terminar edificios, caminos y exclusiones.

## Validación por fases

- Después de cada fase, realizar una captura del viewport y una prueba PIE.
- No considerar una fase verificada si la captura del viewport o la prueba PIE revela errores.
