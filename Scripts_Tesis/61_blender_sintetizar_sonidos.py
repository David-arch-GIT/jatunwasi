# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER/numpy headless) Sintetiza 3 sonidos eerie a medida para las leyendas: Karisiri (drone+susurros), Condenado (lamento con reverb+cadenas), Duende (piedras que caen+risita). WAV mono 44.1kHz, loop-friendly (crossfade).
# Por que se necesito: Dar audio de miedo espacializado a cada aparicion; el usuario no tenia archivos de sonido.
# Resultado obtenido: (pendiente) snd_karisiri/condenado/duende.wav en processed/sonidos.
# ------------------------------------------------------------
import numpy as np, wave, os

SR = 44100
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/sonidos/"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

def t_arr(dur): return np.arange(int(dur*SR))/SR
def sine_ph(freq, dur):
    # freq puede ser escalar o array del largo
    n=int(dur*SR)
    if np.isscalar(freq): freq=np.full(n, float(freq))
    ph=np.cumsum(2*np.pi*freq/SR)
    return np.sin(ph)
def noise(dur): return rng.uniform(-1,1,int(dur*SR))
def box_lp(x, cutoff):
    # lowpass simple por media movil (kernel ~ 1/cutoff)
    k=max(1,int(SR/max(60,cutoff)))
    ker=np.ones(k)/k
    return np.convolve(x, ker, mode='same')
def bandpass(x, lo, hi):
    return box_lp(x, hi) - box_lp(x, lo)
def env_lin(dur, pts):
    # pts = [(t,val),...]
    n=int(dur*SR); e=np.zeros(n); ts=t_arr(dur)
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return np.interp(ts, xs, ys)
def reverb(x, taps=((0.029,0.55),(0.047,0.42),(0.071,0.32),(0.097,0.24),(0.131,0.16))):
    y=x.copy()
    for d,g in taps:
        n=int(d*SR)
        if n<len(x): y[n:]+=x[:-n]*g
    return y
def loopfade(x, xf_s=0.6):
    xf=int(xf_s*SR)
    if xf*2>=len(x): return x
    w=np.linspace(0,1,xf)
    tail=x[-xf:].copy()
    x=x[:-xf].copy()
    x[:xf]=x[:xf]*w + tail*(1-w)
    return x
def norm(x, peak=0.92):
    m=np.max(np.abs(x))+1e-9
    return x/m*peak
def soft(x): return np.tanh(x*1.2)

# ================= KARISIRI: drone + susurros (10 s) =================
def karisiri():
    D=10.0; n=int(D*SR)
    trem=0.5+0.5*np.sin(2*np.pi*0.18*t_arr(D))
    drone=(sine_ph(55,D)+0.7*sine_ph(82.5,D)+0.4*sine_ph(110,D))*0.18*(0.6+0.4*trem)
    # cama de aire
    air=box_lp(noise(D),400)*0.06
    # respiracion/susurro: ruido bandpass modulado por envolvente de respiracion
    breath_env=np.clip(np.sin(2*np.pi*0.28*t_arr(D)-0.4),0,1)**1.5
    whisper=bandpass(noise(D),900,3200)
    whisper*=(breath_env* (0.9+0.2*rng.uniform(-1,1,n)))
    whisper=whisper*0.5
    # jadeo grave a ~5s
    wh=env_lin(D,[(0,0),(4.2,0),(5.0,1),(5.8,0),(D,0)])
    wheeze=bandpass(noise(D),200,700)*wh*0.4
    mix=drone+air+whisper+reverb(whisper*0.5)*0.4+wheeze
    return loopfade(norm(soft(mix)))

# ================= CONDENADO: lamento con reverb + cadenas (12 s) =====
def condenado():
    D=12.0; n=int(D*SR)
    # contorno de gemido (glissando + vibrato)
    base=np.interp(t_arr(D),[0,3,6,9,12],[120,108,150,112,120])
    vib=1+0.03*np.sin(2*np.pi*5.2*t_arr(D))
    tone=sine_ph(base*vib,D)+0.5*sine_ph(base*vib*2,D)+0.25*sine_ph(base*vib*3,D)
    # formantes (vocal 'ahh/ohh')
    form=bandpass(tone,350,700)+0.7*bandpass(tone,800,1300)+0.4*bandpass(tone,2200,2900)
    swell=env_lin(D,[(0,0),(1.5,0.9),(3,0.5),(4.5,1.0),(6.5,0.3),(8,0.9),(10,0.4),(D,0)])
    moan=form*swell*0.5
    # lamento lejano agudo ~7s
    farw=sine_ph(np.interp(t_arr(D),[0,7,8,9,12],[0,300,360,300,0]),D)
    farw*=env_lin(D,[(0,0),(6.6,0),(7.3,0.5),(8.2,0),(D,0)])*0.25
    # cadenas: rafagas metalicas cortas
    chains=np.zeros(n)
    for ct in (2.4,5.1,9.3):
        s=int(ct*SR); ln=int(0.18*SR)
        if s+ln<n:
            burst=bandpass(noise(0.18),2200,5000)*np.exp(-np.linspace(0,6,ln))
            chains[s:s+ln]+=burst*0.35
    mix=moan+farw+chains
    mix=mix+reverb(mix)*0.6   # cavernoso
    return loopfade(norm(soft(mix)))

# ================= DUENDE: piedras + risita (10 s) ===================
def duende():
    D=10.0; n=int(D*SR)
    out=np.zeros(n)
    # viento tenue
    out+=box_lp(noise(D),300)*0.03
    def stone(at):
        s=int(at*SR)
        # doble rebote tk-tk
        for off,g in ((0.0,1.0),(0.06,0.5)):
            ss=s+int(off*SR); ln=int(0.09*SR)
            if ss+ln<n:
                click=bandpass(noise(0.09),1200,6000)*np.exp(-np.linspace(0,9,ln))
                ping=sine_ph(1600,0.09)*np.exp(-np.linspace(0,12,ln))*0.4
                out[ss:ss+ln]+=(click+ping)*g*0.8
    for at in (1.3,3.0,3.2,6.8,8.6):
        stone(at)
    # risita/silbido a ~5s
    gf=np.interp(t_arr(D),[0,4.8,5.2,5.6,6.0,10],[0,1200,1900,1100,1600,0])
    gig=sine_ph(gf*(1+0.06*np.sin(2*np.pi*11*t_arr(D))),D)
    gig*=env_lin(D,[(0,0),(4.7,0),(5.0,0.6),(5.9,0.6),(6.2,0),(D,0)])*0.3
    out+=gig
    # rustle ticks
    for at in (2.2,7.5):
        s=int(at*SR); ln=int(0.05*SR)
        if s+ln<n: out[s:s+ln]+=bandpass(noise(0.05),3000,8000)*np.exp(-np.linspace(0,8,ln))*0.15
    return loopfade(norm(soft(out)))

def write_wav(path, sig):
    sig=np.clip(sig,-1,1)
    data=(sig*32767).astype('<i2').tobytes()
    w=wave.open(path,'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data); w.close()
    return round(len(sig)/SR,2)

res={}
res["karisiri"]=write_wav(OUT+"snd_karisiri.wav", karisiri())
res["condenado"]=write_wav(OUT+"snd_condenado.wav", condenado())
res["duende"]=write_wav(OUT+"snd_duende.wav", duende())
print("SONIDOS OK", res)
