# PLAN DEL RECORRIDO GUIADO — Jatun Wasi Ñawpa Kay

## 1. OBJETIVO
Que el usuario haga un **recorrido estructurado** por el pueblo colonial, guiado por **Adela**, aprendiendo la historia de cada lugar, **sin perderse ni vagar sin rumbo**. Un circuito con inicio, desarrollo y cierre.

## 2. LA RUTA (orden fijo = un circuito lógico)
```
   INICIO (Plaza)
        │  sendero norte
        ▼
   1) TEMPLO  (lo sagrado)
        │  regreso + sendero este
        ▼
   2) CONVENTO  (la fe y el silencio)
        │  sendero oeste
        ▼
   3) HACIENDA  (la vida y la fiesta)
        │  regreso
        ▼
   CIERRE (Plaza)  — despedida
```
**Por qué este orden:** sube de lo sagrado (Templo) a lo comunitario (Convento) a lo doméstico (Hacienda), y cierra volviendo a casa. Geográficamente es un circuito limpio (Templo al norte, Convento al este, Hacienda al oeste — como en el minimapa).

## 3. LAS ETAPAS (qué vive y oye el usuario en cada una)

**ETAPA 0 — Bienvenida (Plaza, inicio):**
Adela recibe al usuario, se presenta ("Soy Adela Zamudio…"), presenta el proyecto en breve y lo invita: *"Sígueme al templo por el sendero."*

**ETAPA 1 — Camino al Templo:**
Mientras avanza por el sendero, Adela narra la **leyenda** del camino (el Karisiri) y le indica el rumbo.

**ETAPA 2 — Antes de entrar al Templo:**
Adela presenta la **arquitectura colonial barroca** (que suene interesante, no plano).

**ETAPA 3 — Dentro del Templo:**
Adela señala los **objetos/tesoros** (retablo de pan de oro, Virgen de Urkupiña) e invita a acercarse a las **cartelas** y a **preguntarle** (IA Convai).

**ETAPAS 4-5-6-7:** se repite el patrón (camino → antes de entrar → adentro) para **Convento** y **Hacienda**.

**ETAPA FINAL — Cierre (Plaza):**
Adela se despide y agradece la visita.

## 4. CÓMO LOGRAR QUE EL USUARIO SIGA LA RUTA (sin desobedecer) 🔑
Cinco capas que se refuerzan — la primera es la más fuerte:

**A. CONTENCIÓN FÍSICA (ya existe en el proyecto) — la clave.**
Los senderos tienen **muros de colisión invisibles** a los lados. El usuario **físicamente no puede salirse** del sendero: solo puede caminar por donde la ruta lo lleva. Esto por sí solo evita el 90% del "vagar". (Ya está construido — ver memoria *paths-state*.)

**B. SIN TELETRANSPORTE (acordado):** el usuario camina a paso normal por el sendero. No puede saltar a lugares al azar.

**C. GUÍA VISUAL:**
- **Minimapa** (recién hecho): le muestra dónde está y a dónde ir.
- **Adela** lo recibe y narra en cada punto (su presencia marca el camino).
- **Letreros de madera** con flechas ("al Templo") en los cruces (ya existen).

**D. GUÍA NARRATIVA (Adela dirige):**
Adela le dice EXPLÍCITAMENTE a dónde ir: *"Ve al templo por el sendero del norte, te espero allí."* El usuario sabe siempre el siguiente paso.

**E. COMPUERTAS SUAVES (opcional, refuerzo):**
Opcional: el siguiente destino se **ilumina / se revela** solo cuando terminas el actual, o Adela recién te invita al siguiente tras completar el presente. Guía el orden sin forzar con rejas.

> **Resumen:** El usuario NO desobedece porque **los muros ya lo contienen** al sendero (A), no hay teletransporte (B), y Adela + el minimapa le dicen a dónde ir (C, D). Es imposible perderse.

## 5. ESTADO: qué está hecho y qué falta
| Pieza | Estado |
|---|---|
| Contención física (muros en senderos) | ✅ hecho |
| Sin teletransporte | ✅ acordado |
| Minimapa que avanza | ✅ hecho |
| Adela guía (modelo + animaciones + voz) | ✅ hecho |
| Voces de narración por etapa | ✅ grabadas (A_nar_*) |
| Letreros/flechas en cruces | ✅ existen |
| **Disparar la narración al llegar a cada punto** | ⚠️ falta cablear (Blueprint, 1 patrón repetido) |
| **IA Convai (preguntar a Adela)** | ⚠️ instalar/configurar (plugin + cerebro ya escrito) |

## 6. LO QUE FALTA, EN ORDEN (para cerrar el recorrido)
1. **Cablear el disparo de narración** en cada punto de la ruta (mismo patrón del BP_GuiaInteractiva que ya hiciste). Lo hacemos juntos, punto por punto.
2. **Convai**: instalar el plugin + pegar el cerebro de Adela (ya te lo di) → responde preguntas.
3. **Prueba final** en el Quest del circuito completo.
