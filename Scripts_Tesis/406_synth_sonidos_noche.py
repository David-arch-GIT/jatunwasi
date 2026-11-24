# 406_synth_sonidos_noche.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: SINTETIZAR (creacion propia, sin licencias de terceros ni descargas) los sonidos de
#   ambiente nocturno: grillos (bucle 12 s sin costura), lechuza lejana (llamado + silencio largo,
#   2 variantes), campanas de bronce (3 golpes con parciales inarmonicos) y pasos sobre grava
#   (bucle de caminata). Salida WAV 16-bit mono 44.1 kHz en Saved/SynthAudio.
# Ejecutar con el Python del motor (solo libreria estandar):
#   "C:/Users/Mi PC/Documents/UE_5.7/Engine/Binaries/ThirdParty/Python3/Win64/python.exe" -I 406_synth_sonidos_noche.py
import math, random, struct, wave, os

SR = 44100
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/SynthAudio"
os.makedirs(OUT, exist_ok=True)
TWO_PI = 2.0 * math.pi

def write_wav(name, buf, peak=0.7):
    m = max(1e-9, max(abs(x) for x in buf))
    g = peak / m
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, x * g)) * 32767)) for x in buf))
    return len(buf) / SR

def lowpass(buf, alpha):
    y = 0.0; out = []
    for x in buf:
        y += alpha * (x - y); out.append(y)
    return out

def biquad_bp(buf, fc, q):
    w0 = TWO_PI * fc / SR; al = math.sin(w0) / (2 * q); cs = math.cos(w0)
    b0, b1, b2 = al, 0.0, -al; a0, a1, a2 = 1 + al, -2 * cs, 1 - al
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    x1 = x2 = y1 = y2 = 0.0; out = []
    for x in buf:
        y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y; out.append(y)
    return out

def echoes(buf, taps):
    out = buf[:] + [0.0] * int(max(d for d, g in taps) * SR + 10)
    for d, g in taps:
        k = int(d * SR)
        for i, x in enumerate(buf):
            out[i + k] += x * g
    return out

# ---------------- GRILLOS (bucle 12 s, costura perfecta por indice modular) ----------------
def grillos():
    random.seed(406)
    L = 12.0; N = int(L * SR); buf = [0.0] * N
    def voice(f, period, npulse, amp, plen=0.018, pgap=0.022):
        off = random.uniform(0, period); t0 = off
        while t0 < L:
            tc = t0 + random.uniform(-0.04, 0.04)
            for p in range(npulse):
                st = tc + p * (plen + pgap); n = int(plen * SR); s0 = int(st * SR)
                fm = f * (1.0 + random.uniform(-0.01, 0.01))
                for i in range(n):
                    e = math.sin(math.pi * i / n) ** 2
                    idx = (s0 + i) % N
                    buf[idx] += math.sin(TWO_PI * fm * ((s0 + i) / SR)) * e * amp
            t0 += period
    for _ in range(7):
        voice(random.uniform(3900, 5200), random.uniform(0.55, 1.1), random.randint(2, 4), random.uniform(0.10, 0.22))
    for _ in range(18):  # coro lejano
        voice(random.uniform(3600, 5600), random.uniform(0.35, 0.9), random.randint(2, 4), random.uniform(0.015, 0.035))
    buf = lowpass(buf, 0.55)
    return write_wav("SW_Grillos_Loop", buf, 0.55)

# ---------------- LECHUZA (llamado lejano + silencio; bucle 30 s) ----------------
def lechuza(name, call_at, f0, seed):
    random.seed(seed)
    L = 30.0; N = int(L * SR); buf = [0.0] * N
    notes = [(0.00, 0.38, 1.00), (0.62, 0.20, 0.80), (0.94, 0.20, 0.85), (1.24, 0.75, 1.00)]
    nz = 0.0
    for (st, dur, a) in notes:
        s0 = int((call_at + st) * SR); n = int(dur * SR); ph = 0.0
        for i in range(n):
            t = i / SR; x = t / dur
            att = min(1.0, t / 0.05); rel = min(1.0, (dur - t) / 0.16)
            env = max(0.0, min(att, rel)) ** 1.2
            f = f0 * (1.0 + 0.06 * math.sin(math.pi * x) - 0.04 * x) * (1.0 + 0.004 * math.sin(TWO_PI * 5.5 * t))
            ph += TWO_PI * f / SR
            nz += 0.08 * (random.uniform(-1, 1) - nz)
            v = math.sin(ph) + 0.22 * math.sin(2 * ph) + 0.06 * math.sin(3 * ph) + 0.35 * nz
            buf[s0 + i] += v * env * a
    buf = lowpass(buf, 0.22)
    buf = echoes(buf, [(0.19, 0.28), (0.41, 0.14), (0.67, 0.07)])[:N]
    return write_wav(name, buf, 0.5)

# ---------------- CAMPANAS (3 golpes de bronce) ----------------
def campanas():
    random.seed(4061)
    L = 14.0; N = int(L * SR); buf = [0.0] * N
    f0 = 146.8
    partials = [(0.5, 0.55, 9.0), (1.0, 0.80, 6.5), (1.19, 0.55, 4.5), (1.5, 0.38, 3.4), (2.0, 0.95, 3.0),
                (2.51, 0.30, 2.0), (3.0, 0.42, 1.6), (4.07, 0.25, 1.1), (5.33, 0.12, 0.7)]
    for strike in (0.0, 2.7, 5.4):
        s0 = int(strike * SR)
        for (r, a, dec) in partials:
            f1 = f0 * r; f2 = f1 + 0.6
            n = min(N - s0, int(dec * 4.5 * SR))
            for i in range(n):
                t = i / SR; e = math.exp(-t / dec) * min(1.0, t / 0.004)
                buf[s0 + i] += a * e * 0.5 * (math.sin(TWO_PI * f1 * t) + math.sin(TWO_PI * f2 * t))
        for i in range(int(0.012 * SR)):  # golpe del badajo
            buf[s0 + i] += random.uniform(-1, 1) * 0.4 * (1 - i / (0.012 * SR))
    buf = echoes(buf, [(0.07, 0.22), (0.13, 0.16), (0.23, 0.11), (0.37, 0.07)])[:N]
    return write_wav("SW_Campanas_Templo", buf, 0.8)

# ---------------- PASOS EN GRAVA (bucle de caminata, 4 pasos) ----------------
def pasos():
    random.seed(4062)
    step = 0.57; L = step * 4; N = int(L * SR); buf = [0.0] * N
    def burst(s0, dur, amp, density):
        n = int(dur * SR); raw = [0.0] * n
        for i in range(n):
            if random.random() < density / SR:
                g = random.uniform(0.3, 1.0); k = random.randint(20, 120)
                for j in range(min(k, n - i)):
                    raw[i + j] += random.uniform(-1, 1) * g * (1 - j / k)
            raw[i] += random.uniform(-1, 1) * 0.15
        env = [math.sin(math.pi * min(1.0, i / n)) ** 0.7 * math.exp(-3.0 * i / n) for i in range(n)]
        raw = [r * e for r, e in zip(raw, env)]
        raw = biquad_bp(raw, random.uniform(1500, 2400), 0.8)
        for i, x in enumerate(raw):
            buf[(s0 + i) % N] += x * amp
        for i in range(int(0.035 * SR)):  # golpe sordo
            t = i / SR
            buf[(s0 + i) % N] += math.sin(TWO_PI * 85 * t) * math.exp(-t / 0.012) * amp * 0.6
    for k in range(4):
        s0 = int((k * step + random.uniform(-0.02, 0.02)) * SR)
        burst(s0, 0.045, random.uniform(0.8, 1.0), 2200)
        burst(s0 + int(0.075 * SR), 0.09, random.uniform(0.6, 0.85), 1800)
    return write_wav("SW_Pasos_Grava_Loop", buf, 0.6)

if __name__ == "__main__":
    print("grillos", round(grillos(), 2))
    print("lechuza1", round(lechuza("SW_Lechuza_Lejana_A", 3.0, 400.0, 11), 2))
    print("lechuza2", round(lechuza("SW_Lechuza_Lejana_B", 17.0, 355.0, 12), 2))
    print("campanas", round(campanas(), 2))
    print("pasos", round(pasos(), 2))
