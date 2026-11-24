# 433_synth_pozo_susurro_canto.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: SINTETIZAR (creacion propia, sin descargas) 3 sonidos nuevos:
#   - SW_Pozo_Moneda: tintineo de la moneda + caida ~1.1 s + chapoteo con eco largo de pozo profundo
#   - SW_Susurro_Leyenda: susurro inquietante (ruido respirado filtrado por formantes de vocales,
#     silabas irregulares) + zumbido grave; para cuando el visitante mira fijo a una criatura
#   - SW_Canto_Convento_Loop: "canto llano" lejano (coro masculino sintetico: pulsos glotales filtrados
#     por formantes de 'a/o', melodia en modo dorico, 2 voces, reverberacion de nave) bucle 32 s
# Ejecutar con el Python del motor: python.exe -I 433_synth_pozo_susurro_canto.py
import math, random, struct, wave, os
SR = 44100; TP = 2 * math.pi
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/SynthAudio"
os.makedirs(OUT, exist_ok=True)

def save(name, buf, peak=0.8):
    m = max(1e-9, max(abs(x) for x in buf)); g = peak / m
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * g)) * 32767)) for x in buf))
    print(name, round(len(buf) / SR, 2))

def bp(buf, fc, q):
    w0 = TP * fc / SR; al = math.sin(w0) / (2 * q); cs = math.cos(w0); a0 = 1 + al
    b0, b2, a1, a2 = al / a0, -al / a0, -2 * cs / a0, (1 - al) / a0
    x1 = x2 = y1 = y2 = 0.0; o = []
    for x in buf:
        y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2; x2, x1, y2, y1 = x1, x, y1, y; o.append(y)
    return o

def lp(buf, a):
    y = 0.0; o = []
    for x in buf: y += a * (x - y); o.append(y)
    return o

def reverb(buf, taps, tail=1.0):
    out = buf[:] + [0.0] * int(tail * SR)
    for d, g in taps:
        k = int(d * SR)
        for i, x in enumerate(buf):
            if i + k < len(out): out[i + k] += x * g
    return out

def comb_verb(buf, delays, fb, tail):
    out = buf[:] + [0.0] * int(tail * SR); acc = [0.0] * len(out)
    for d in delays:
        k = int(d * SR); line = out[:]
        for i in range(k, len(line)):
            line[i] = out[i] + line[i - k] * fb
        for i in range(len(acc)): acc[i] += line[i] / len(delays)
    return acc

# ---------------- moneda al pozo ----------------
def moneda():
    random.seed(433); N = int(4.5 * SR); b = [0.0] * N
    for f, a, d in ((5200, 1.0, 0.25), (7900, 0.6, 0.18), (11300, 0.35, 0.12), (3100, 0.4, 0.3)):   # tintineo
        for i in range(int(0.9 * SR)):
            t = i / SR; b[i] += a * math.exp(-t / d) * math.sin(TP * f * t) * 0.5
    s0 = int(1.15 * SR)                                                                         # chapoteo
    sp = [random.uniform(-1, 1) * math.exp(-i / (0.05 * SR)) for i in range(int(0.25 * SR))]
    sp = bp(sp, 900, 1.2)
    for i, x in enumerate(sp): b[s0 + i] += x * 1.6
    for i in range(int(0.35 * SR)):                                                             # 'plop' con barrido
        t = i / SR; f = 480 + 900 * t
        b[s0 + i] += 0.9 * math.exp(-t / 0.07) * math.sin(TP * f * t)
    for k in range(6):                                                                          # gotas
        g0 = s0 + int((0.18 + k * 0.11 + random.uniform(0, 0.05)) * SR)
        for i in range(int(0.06 * SR)):
            t = i / SR; f = random.uniform(900, 1600) + 4000 * t
            if g0 + i < N: b[g0 + i] += 0.25 * math.exp(-t / 0.02) * math.sin(TP * f * t)
    b = comb_verb(b, [0.047, 0.061, 0.073, 0.089], 0.72, 0.5)[:N]
    save("SW_Pozo_Moneda", b, 0.85)

# ---------------- susurro ----------------
def susurro():
    random.seed(4331); L = 3.2; N = int(L * SR); out = [0.0] * N
    vowels = [(700, 1200), (400, 2200), (500, 900), (300, 2400), (600, 1000)]
    t = 0.15
    while t < L - 0.4:
        dur = random.uniform(0.12, 0.32); n = int(dur * SR); s0 = int(t * SR)
        f1, f2 = random.choice(vowels)
        nz = [random.uniform(-1, 1) for _ in range(n)]
        sh = bp(nz, random.uniform(3500, 6000), 2.0)                     # 's/sh' sibilante
        v = [a + b2 * 0.8 for a, b2 in zip(bp(nz, f1, 6), bp(nz, f2, 8))]  # vocal susurrada
        for i in range(n):
            e = math.sin(math.pi * i / n) ** 1.5
            mix = (sh[i] * 0.5 if i < n * 0.35 else 0) + v[i] * 1.6
            out[s0 + i] += mix * e
        t += dur + random.uniform(0.05, 0.25)
    for i in range(N):                                                    # zumbido grave inquietante
        tt = i / SR; out[i] += 0.05 * math.sin(TP * 55 * tt + 2 * math.sin(TP * 0.3 * tt)) * min(1, tt / 0.8) * min(1, (L - tt) / 0.6)
    out = reverb(out, [(0.05, 0.4), (0.11, 0.3), (0.19, 0.2), (0.31, 0.12)], 0.6)
    save("SW_Susurro_Leyenda", out, 0.7)

# ---------------- canto llano lejano (bucle 32 s) ----------------
def canto():
    random.seed(4332); L = 32.0; N = int(L * SR); out = [0.0] * N
    D = 146.83  # Re3 (modo dorico sobre Re)
    scale = [0, 2, 3, 5, 7, 9, 10, 12]
    melody = [0, 0, 2, 3, 2, 0, 5, 4, 3, 2, 3, 2, 0, 0, -1, 0]   # grados; -1 = Do
    beats = [2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 4]
    unit = L / sum(beats)
    form = {"a": [(700, 1.0, 80), (1150, 0.5, 90), (2600, 0.12, 120)], "o": [(450, 1.0, 70), (800, 0.6, 80), (2500, 0.08, 120)]}
    t = 0.0
    for deg, bt in zip(melody, beats):
        dur = bt * unit; s0 = int(t * SR); n = int(dur * SR)
        semis = -2 if deg == -1 else scale[deg]
        for voice, (oct_mul, amp) in enumerate(((1.0, 1.0), (0.5, 0.55))):   # tenor + bajo a la octava
            f0 = D * oct_mul * 2 ** (semis / 12.0)
            vow = form["a" if (voice + deg) % 2 == 0 else "o"]
            ph = 0.0; src = []
            for i in range(n):
                tt = i / SR
                f = f0 * (1 + 0.004 * math.sin(TP * 5.0 * tt + voice))           # vibrato leve
                ph += f / SR
                src.append((ph % 1.0) * 2 - 1)                                       # pulso glotal (diente de sierra)
            src = lp(src, 0.35)
            v = [0.0] * n
            for fc, g, bw in vow:
                band = bp(src, fc, fc / bw)
                for i in range(n): v[i] += band[i] * g
            for i in range(n):
                tt = i / SR; e = min(1, tt / 0.25) * min(1, (dur - tt) / 0.3)
                out[(s0 + i) % N] += v[i] * e * amp
        t += dur
    out = comb_verb(out, [0.113, 0.137, 0.159, 0.181], 0.78, 0.0)[:N]   # nave de piedra (circular por bucle)
    out = lp(out, 0.5)
    save("SW_Canto_Convento_Loop", out, 0.6)

moneda(); susurro(); canto()
