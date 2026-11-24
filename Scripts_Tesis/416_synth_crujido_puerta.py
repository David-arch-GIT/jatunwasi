# 416_synth_crujido_puerta.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: SINTETIZAR (creacion propia, sin descargas) el sonido de una puerta colonial de madera
#   pesada al abrirse/cerrarse: chasquido del cerrojo + crujido de bisagra (friccion stick-slip:
#   tren de impulsos con frecuencia que deriva, filtrado por resonancias de madera) + golpe sordo.
#   WAV 16-bit mono 44.1 kHz, ~2.2 s, en Saved/SynthAudio/SW_Puerta_Crujido.wav
# Ejecutar con el Python del motor: python.exe -I 416_synth_crujido_puerta.py
import math, random, struct, wave, os
SR = 44100; TWO_PI = 2 * math.pi
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/SynthAudio"
os.makedirs(OUT, exist_ok=True)

def biquad_bp(buf, fc, q):
    w0 = TWO_PI * fc / SR; al = math.sin(w0) / (2 * q); cs = math.cos(w0)
    a0 = 1 + al; b0, b2 = al / a0, -al / a0; a1, a2 = -2 * cs / a0, (1 - al) / a0
    x1 = x2 = y1 = y2 = 0.0; out = []
    for x in buf:
        y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y; out.append(y)
    return out

random.seed(416)
L = 2.2; N = int(L * SR); exc = [0.0] * N
# 1) cerrojo (0.00-0.05 s): dos clics metalicos
for t0, a in ((0.010, 1.0), (0.045, 0.6)):
    s0 = int(t0 * SR)
    for i in range(int(0.006 * SR)):
        exc[s0 + i] += random.uniform(-1, 1) * a * (1 - i / (0.006 * SR))
# 2) crujido de bisagra (0.15-1.75 s): impulsos stick-slip, frecuencia 18->55->30 Hz, amplitud ondulante
t = 0.15; ph = 0.0
while t < 1.75:
    x = (t - 0.15) / 1.6
    f = 18 + 37 * math.sin(math.pi * min(1.0, x * 1.3)) + 6 * math.sin(TWO_PI * 2.3 * t)
    amp = (0.35 + 0.65 * math.sin(math.pi * x)) * (0.7 + 0.3 * random.random())
    s0 = int(t * SR)
    for i in range(30):
        if s0 + i < N:
            exc[s0 + i] += amp * (1 - i / 30.0) * (1 if i % 2 == 0 else -0.6)
    t += 1.0 / f * random.uniform(0.85, 1.15)
# 3) madera: resonancias del panel
mix = [0.0] * N
for fc, q, g in ((420, 6, 1.0), (880, 8, 0.7), (1650, 10, 0.45), (2900, 12, 0.25), (190, 4, 0.6)):
    band = biquad_bp(exc, fc, q)
    for i in range(N):
        mix[i] += band[i] * g
# 4) golpe sordo final del batiente (1.80 s)
s0 = int(1.80 * SR)
for i in range(int(0.3 * SR)):
    if s0 + i < N:
        tt = i / SR
        mix[s0 + i] += 0.9 * math.exp(-tt / 0.06) * (math.sin(TWO_PI * 70 * tt) + 0.5 * math.sin(TWO_PI * 143 * tt))
# fundido final y normalizacion
for i in range(int(0.08 * SR)):
    mix[N - 1 - i] *= i / (0.08 * SR)
m = max(abs(v) for v in mix); g = 0.8 / m
with wave.open(os.path.join(OUT, "SW_Puerta_Crujido.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v * g)) * 32767)) for v in mix))
print("puerta", L)
