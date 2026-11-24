# Guía — Narración por voz al entrar al camino (relatos)

## Qué ya quedó hecho por script (no tocar)
- 4 voces generadas (voz Sabina) e importadas a Unreal:
  `/Game/JWN/Audio/Relatos/A_Relato_plaza / _hacienda / _convento / _templo`
- 4 puntos colocados en las entradas: actores **RELATO_plaza, RELATO_hacienda, RELATO_convento, RELATO_templo**
  - Trigger esférico de 7.5 m (dispara al acercarse por el camino)
  - Voz ya asignada a cada uno, **sin espacializar** (suena en tus oídos, como narración)

## Único paso manual (una vez, ~2 min) — cablear BP_NarrationPoint
Esto hace que al entrar se reproduzca la voz **una sola vez**.

1. Content Browser → `/Game/JWN/Blueprints` → doble clic en **BP_NarrationPoint**.
2. Arriba, pestaña **Event Graph**.
3. Panel **Components** (izquierda): clic en **TriggerVolume**.
   En **Details** (derecha), baja hasta **Events** → clic en el **+** verde de
   **On Component Begin Overlap**. Aparece el nodo evento en el grafo.
4. Arrastra el componente **Narration** desde el panel Components al grafo → suelta →
   elige **Get Narration**.
5. Desde el pin azul de **Narration**, arrastra y busca **Play** (Play - AudioComponent).
6. Conecta la flecha blanca de ejecución del evento **On Component Begin Overlap** → al nodo **Play**.
7. Para que suene SOLO UNA VEZ: arrastra **TriggerVolume** al grafo (Get) → desde su pin
   arrastra y busca **Set Collision Enabled** → en el desplegable elige **No Collision**.
   Conecta la flecha de salida de **Play** → a **Set Collision Enabled**.
8. Botón **Compile** (arriba izquierda) → **Save**.

Resultado: al caminar hacia cada escenario, entras al radio y escuchas el relato de esa zona,
una sola vez. Se hereda automáticamente a los 4 puntos.

## Prueba (PIE)
Juega (PIE) y camina hacia la hacienda / convento / templo / al centro de la plaza:
debe arrancar la voz al entrar al radio, y no repetirse si vuelves a pasar.
