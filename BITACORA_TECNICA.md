# Bitácora técnica — JatunWasi Ñawpaqay

Registro técnico acumulativo del proyecto de tesis (recreación VR del patrimonio colonial de Tarata, Cochabamba). Documento de trabajo: se añaden entradas nuevas al final sin borrar las anteriores. Motor: Unreal Engine 5.7. Plataforma objetivo: Meta Quest 2 en modo autónomo (renderizado forward móvil). Mapa principal: `MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN`.

---

## 1. Criterio de iluminación nocturna

- **Ambiente:** noche cerrada con contraste cromático deliberado — luz de luna azul fría contra fuentes cálidas anaranjadas (faroles, velas, apliques). Ese contraste es una decisión artística fija y no debe alterarse.
- **Regla de oro:** pocas luces reales bien colocadas y mucho material emisivo. Las fuentes visibles (faroles, ventanas, velas) se resuelven con materiales Unlit emisivos; la luz real solo se usa donde debe caer sobre muros y piso.
- **Sin horneado (bake):** la iluminación es totalmente dinámica. No se hornea porque buena parte de la geometría proviene de mallas GLB sin canal de UV para lightmap, y hornear sobre ellas produciría errores. En su lugar se controla el costo con radios cortos, corte por distancia y ausencia de sombras.
- **Exposición bloqueada:** una única exposición para todo el mapa, fija, para evitar que la cámara "bombee" el brillo al girar la cabeza en VR.
- **Perillas globales finales:** EV100 (mínimo = máximo) 0.0; SkyLight 0.22; Luna (MoonLight) 0.7; Bloom 0.32. Número de EV100 más bajo = escena más clara.

## 2. Restricciones de Quest 2 y decisiones descartadas

- **Límite de luces por objeto/tile:** el renderizado forward móvil procesa aproximadamente cuatro luces dinámicas por objeto. Si un punto recibe más, el motor descarta las sobrantes y va cambiando cuáles ignora según el ángulo de cámara, produciendo parpadeo de luces en el visor. Por eso el solapamiento máximo de cuatro luces por punto es una restricción de hardware, no una preferencia.
- **Sin sombras dinámicas en luces point/spot:** solo la luz direccional (luna) proyecta sombra.
- **Radios:** interiores 400 a 600 (hasta 850 en salas grandes); exteriores hasta 900; nunca por encima de 1200.
- **Corte por distancia (Max Draw Distance) obligatorio:** interiores 1800 con desvanecido 400; exteriores 3500 con desvanecido 500.
- **Prohibido en este proyecto:** Lumen y GI, niebla volumétrica, Rect Lights, funciones de luz e IES, sombras en point/spot, Real Time Capture en el SkyLight, reflexiones en espacio de pantalla (SSR), oclusión ambiental en espacio de pantalla (SSAO) y Bloom por encima de 0.6.
- **Descartado por inviabilidad técnica:** ventanas emisivas encendidas mediante losas (ver punto 3.6); horneado de iluminación (ver punto 1).

## 3. Problemas encontrados y su solución

### 3.1 Exposición automática que "bombea" en VR
La exposición automática cambiaba el brillo al mirar zonas claras u oscuras, lo que en el visor produce mareo. Solución: PostProcessVolume sin límites (Unbound) con método Histograma y con el mínimo y el máximo de EV100 igualados, lo que congela la exposición. Se probó el modo Manual y dejaba la escena en negro; se descartó. Valor final EV100 mínimo = máximo = 0.0.

### 3.2 "Apply Physical Camera Exposure" activado
El PostProcess tenía activada la exposición por cámara física, que reintroducía variación de brillo pese al bloqueo anterior. Se desactivó.

### 3.3 SkyLight filtrándose a los interiores
El SkyLight, con intensidad alta, inundaba los interiores con un gris azulado plano y sin volumen, restando el contraste cálido buscado. Solución: reducir su intensidad de 0.40 a 0.22, conservando el tinte azul frío para exteriores.

### 3.4 Emisivos quemados por el Bloom
Con el Bloom alto, los materiales emisivos (velas, brasas, faroles) se lavaban y perdían forma. Solución: reducir intensidades emisivas (vela de 5 a 2, brasa de 3 a 1.5, farol cálido de 8 a 5) y bajar el Bloom de 0.45 a 0.32.

### 3.5 Luces mal ancladas por script
Varias luces colocadas por script quedaron en posiciones aproximadas (por ejemplo, las arañas del salón de baile contra el muro sur en lugar del centro de la sala, y el relleno de la sala de folklore a varios metros de las vitrinas reales). Se detectaron consultando las posiciones reales de los props y se reubicaron.

### 3.6 Ventanas emisivas descartadas
Se intentó simular ventanas encendidas con losas emisivas. Quedaban flotando dentro de las habitaciones y a la altura equivocada; la malla de ventanas de la Hacienda no tiene un plano de vidrio (sus materiales son madera, estuco y piedra), por lo que no puede encenderse por material. Se descartaron por completo. El usuario decidió finalmente no usar ventanas emisivas.

### 3.7 Marcadores de narración demasiado brillantes
Los marcadores de puntos de narración se veían como esferas blancas grandes de noche. Se redujo el valor emisivo de su material para que se lean como un punto guía tenue sin competir con los faroles.

### 3.8 Episodio de 141 luces reducidas y luego recuperadas
El usuario densificó manualmente la iluminación hasta 141 luces, lo que produjo hasta 12 luces solapadas en un punto de la Hacienda (muy por encima del límite de cuatro). Se adelgazó a 59 (quedó escaso), luego se recuperó el arreglo denso desde un autosave y se reparó con orden de menos a más destructivo (reducir radios, retirar las menos importantes dejando su prop emisivo, y borrar solo duplicados). Resultado: 105 luces con solapamiento máximo de cuatro en todas las zonas. Solo la Hacienda no admitió todas sus luces por ser un ala de dos pisos apilados sin oclusión entre niveles.

## 4. Estado de respaldos

- `MAP_..._BACKUP_PRE_LUCES`: estado previo a toda la iluminación.
- `MAP_..._BACKUP_LUCES_FINAL`: respaldo de la iluminación automática (105 luces).
- `MAP_..._BACKUP_LUCES_USUARIO`: estado de la iluminación recolocada a mano por el usuario (el bueno).
- Autosaves del editor en `Saved/Autosaves`: utilizados una vez para recuperar el arreglo denso de luces.

## 5. Recolocación manual de luces interiores (usuario)

Tras el ajuste automático, el usuario recolocó a mano las luces de los interiores de la Hacienda hasta dejarlas a su gusto (estado respaldado como `BACKUP_LUCES_USUARIO`, referencia 111 luces). Queda establecida una regla permanente: no se modifica ninguna luz (posición, intensidad, radio, color ni globales) ni los props de iluminación ni sus materiales emisivos. Si una optimización requiere tocar una luz, se omite y se anota.

## 6. Optimizaciones para Quest 2 (sin tocar luces)

- **Texturas a 2K:** 164 texturas por encima de 2K limitadas a 2048. Memoria reducida de ~2340 MB a ~582 MB.
- **LODs automáticos:** generados en las 172 mallas que no los tenían. Árboles confirmados con impostor en el último LOD.
- **Corte de distancia al follaje:** aplicado a 229 componentes instanciados.
- **Cull Distance Volume:** probado y retirado porque ocultaba arquitectura lejana.
- **Cull por objeto a props:** no había props sueltos (la decoración es instanciada o arquitectura). Props de iluminación excluidos.
- **Mallas duplicadas:** una detectada (PLZP_CanastaChuno y su _Fix en el origen), no borrada.
- **Materiales:** 7 con recorte (follaje, impostores) y 12 translúcidos (vidrio, brillos, decals); no se modificaron.
- Tras cada optimización se verificó que las luces seguían idénticas.

## 7. Locomoción VR

Locomoción continua por proyección a NavMesh (el pawn BP_XRPawn no tiene cápsula de colisión; el recorrido se contiene con el NavMesh). Probada en Oculus: cómoda. Pendiente: el desplazamiento lateral (Get Right Vector) no está construido; el avance va en la dirección de la cámara.

## 8. Correcciones tras la primera prueba en Oculus

- **Horizonte plano / follaje que no cargaba al fondo:** los cortes de distancia del follaje estaban demasiado cortos (árboles, rocas y suelo empedrado a 60 m; arbustos a 35; pasto a 20), por lo que el bosque de fondo desaparecía. Se corrigieron generosos y por categoría: suelo, árboles y cercas ya no se cortan (los árboles usan su impostor a distancia, barato), rocas a 250 m, arbustos y jardines a 150 m, pasto a 80 m. El bosque ahora carga hasta el horizonte. Si el rendimiento lo pide, se puede acercar el corte de pasto y arbustos sin afectar la línea de árboles del fondo.
- **Puertas de la Hacienda que bloqueaban el paso:** al moverse por NavMesh, el bloqueo venía de que la navegación no conectaba a través de los vanos, agravado en el segundo piso porque sus muros usaban colisión por defecto. Se puso la colisión de los muros del segundo piso en modo complejo (respeta los huecos) y se reconstruyó el NavMesh. Verificado con pruebas de ruta: las cuatro rutas que cruzan puertas devuelven camino navegable válido.

Ninguna de las dos correcciones tocó luces (109 luces point/spot intactas, verificado en cada paso). Scripts registrados en `Scripts_Tesis\` (35 a 39).

## 9. Pendientes técnicos conocidos

- Ramal lateral (strafe) de la locomoción: pendiente de cablear a mano en BP_XRPawn (Python en UE 5.7 no crea ni conecta nodos de Blueprint).
- Medición real de fps y triángulos en el visor (stat unit, stat rhi), sobre todo tras hacer generoso el follaje.
- Antes de empaquetar debe desactivarse el plugin MCPUnreal, porque su puerto 8090 hace fallar el cook.
