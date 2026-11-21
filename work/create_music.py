from pathlib import Path
import numpy as np
from scipy.signal import butter,sosfilt
import wave,json
R=Path(r'D:\tiktokAnimasyon');OUT=R/'app/audio';OUT.mkdir(exist_ok=True)
FS=44100;BPM=112;BEAT=60/BPM;BEATS=128;N=round(BEATS*BEAT*FS);rng=np.random.default_rng(112)
drums=np.zeros(N,dtype=np.float64);lead=np.zeros(N,dtype=np.float64);drone=np.zeros(N,dtype=np.float64)
def place(track,sound,beat,gain=1):
 start=round(beat*BEAT*FS);indices=(np.arange(len(sound))+start)%N
 np.add.at(track,indices,sound*gain)
def lowpass(sound,hz):return sosfilt(butter(3,hz,fs=FS,output='sos'),sound)
def dum(velocity=1):
 t=np.arange(round(.65*FS))/FS
 freq=55+70*np.exp(-t*35);phase=np.cumsum(freq)*2*np.pi/FS
 body=np.sin(phase)*np.exp(-t*9)+.25*np.sin(phase*1.73)*np.exp(-t*18)
 hit=lowpass(rng.normal(size=len(t)),3400)*np.exp(-t*95)*.18
 return np.tanh((body+hit)*1.1)*velocity*.5

def tek(velocity=1):
 t=np.arange(round(.23*FS))/FS;noise=rng.normal(size=len(t));noise=noise-lowpass(noise,900);noise=lowpass(noise,7000)
 click=np.sin(2*np.pi*960*t)*np.exp(-t*46)+.3*np.sin(2*np.pi*1810*t)*np.exp(-t*70)
 return (noise*np.exp(-t*30)*.27+click*.19)*velocity

# An original two-bar davul pattern, with restrained fills on phrase endings.
for bar in range(32):
 base=bar*4
 for at,kind,vel in [(0,'d',1),(.75,'t',.40),(1,'t',.75),(1.5,'t',.42),(2,'d',.82),(2.5,'t',.5),(3,'t',.72),(3.5,'t',.35)]:
  place(drums,dum(vel) if kind=='d' else tek(vel),base+at)
 if bar%4==3:
  for at,vel in [(3.25,.35),(3.75,.48)]:place(drums,tek(vel),base+at)

# Newly composed Hicaz-coloured phrases (D, Eb, F#, G, A, Bb, C, D).
scale=[0,1,4,5,7,8,10,12,13,16]
phrases=[
 [(4,.5),(3,.5),(2,1),(1,.5),(2,.5),(0,1)],
 [(0,.5),(1,.5),(2,.5),(3,.5),(4,1),(3,.5),(2,.5)],
 [(4,.5),(5,.5),(6,.5),(7,.5),(6,.5),(5,.5),(4,1)],
 [(3,.5),(2,.5),(1,.5),(2,.5),(0,2)],
 [(7,.75),(6,.25),(5,.5),(4,.5),(5,.5),(4,.5),(3,1)],
 [(4,.5),(3,.5),(2,.5),(1,.5),(2,1),(0,1)],
 [(2,.5),(3,.5),(4,1),(3,.5),(2,.5),(1,1)],
 [(2,.5),(1,.5),(0,1),(1,.5),(2,.5),(0,1)]
]

def zurna(degree,length,accent=1,ornament=False):
 dur=length*BEAT;release=.055;t=np.arange(round((dur+release)*FS))/FS
 hz=293.6648*2**(scale[degree]/12)
 vibrato=.0037*np.sin(2*np.pi*5.4*t)*np.minimum(t/.12,1)
 grace=0 if not ornament else .018*np.exp(-t*35)*np.sin(t*200)
 freq=hz*(1+vibrato+grace);phase=np.cumsum(freq)*2*np.pi/FS
 tone=np.zeros_like(t)
 for harmonic in range(1,15):
  # Reed-like harmonic body, reduced upper partials to keep the tone comfortable.
  formant=1+.75*np.exp(-((harmonic*hz-1600)/700)**2)
  weight=formant/harmonic**1.35*(1 if harmonic*hz<6000 else .25)
  tone+=np.sin(phase*harmonic+.05*np.sin(t*18))*weight
 tone=np.tanh(tone*.75)
 env=np.minimum(t/.014,1)*np.clip((dur+release-t)/release,0,1)
 env*=.94+.04*np.sin(2*np.pi*4.8*t)
 breath=lowpass(rng.normal(size=len(t)),5200)*.012
 return (tone*.18+breath)*env*accent

for bar in range(32):
 phrase=phrases[bar%8];beat=bar*4
 for i,(degree,length) in enumerate(phrase):
  # Slightly different articulation over each eight-bar section.
  accent=.93+(.07 if i==0 else 0)+(.04 if 16<=bar<24 else 0)
  place(lead,zurna(degree,length,accent,ornament=(length>=.75 and bar%2==0)),beat)
  beat+=length

# Quiet tonic/fifth underpinning; per-bar swells, no imported samples.
t=np.arange(N)/FS
swells=.55+.45*np.sin(np.pi*((t/BEAT)%4)/4)**2
drone=(np.sin(2*np.pi*146.8324*t)+.45*np.sin(2*np.pi*220*t))*.014*swells
# Circular room tails preserve the loop boundary.
leadL=lead+np.roll(lead,round(.071*FS))*.12+np.roll(lead,round(.151*FS))*.07
leadR=lead+np.roll(lead,round(.089*FS))*.12+np.roll(lead,round(.181*FS))*.07
room=drums+np.roll(drums,round(.043*FS))*.07
full=np.column_stack([room*.68+leadL+drone,room*.68+leadR+drone])
full=np.tanh(full*1.25)
peak=float(np.max(np.abs(full)));full*=.89/peak
percussion=np.column_stack([room,room]);percussion*=.80/np.max(np.abs(percussion))

def save(name,audio):
 pcm=np.round(np.clip(audio,-1,1)*32767).astype('<i2')
 with wave.open(str(OUT/name),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(FS);f.writeframes(pcm.tobytes())
 return {'peak':float(np.max(np.abs(audio))),'rms':float(np.sqrt(np.mean(audio**2))),'seconds':len(audio)/FS,'frames':len(audio)}
report={'full':save('meydan-halay-112.wav',full),'drums':save('davul-112.wav',percussion)}
# A short shareable audition, with a gentle fade at the end.
preview=full[:round(16*BEAT*FS)].copy();fade=round(.35*FS);preview[-fade:]*=np.linspace(1,0,fade)[:,None]
save('halay-onizleme.wav',preview)
metadata={'title':'Meydan Halayı','bpm':BPM,'beats':BEATS,'sample_rate':FS,'loop_seconds':N/FS,'provenance':'Bu proje için sıfırdan sentezlenen özgün melodi ve davul; dış kayıt veya sample kullanılmadı.','tracks':{'halay':'/assets/audio/meydan-halay-112.wav','drum':'/assets/audio/davul-112.wav'},'report':report}
(OUT/'music.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'runtime/music-render.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report))
