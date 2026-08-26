import math, json

# ---------- color math (sRGB <-> CIELAB) ----------
def _s2l(c):
    c/=255.0
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def _l2s(c):
    v = c*12.92 if c<=0.0031308 else 1.055*(c**(1/2.4))-0.055
    return max(0,min(255,round(v*255)))
def unhex(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def hx(rgb): return '#%02X%02X%02X'%tuple(rgb)

M  = [[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]]
MI = [[3.2404542,-1.5371385,-0.4985314],[-0.9692660,1.8760108,0.0415560],[0.0556434,-0.2040259,1.0572252]]
WP = (0.95047,1.0,1.08883)
def rgb2lab(rgb):
    r,g,b=[_s2l(c) for c in rgb]
    xyz=[M[i][0]*r+M[i][1]*g+M[i][2]*b for i in range(3)]
    f=[]
    for i,v in enumerate(xyz):
        t=v/WP[i]
        f.append(t**(1/3) if t>216/24389 else (841/108)*t+4/29)
    return (116*f[1]-16, 500*(f[0]-f[1]), 200*(f[1]-f[2]))
def lab2rgb(lab):
    L,a,bb=lab
    fy=(L+16)/116; fx=fy+a/500; fz=fy-bb/200
    def inv(t):
        return t**3 if t**3>216/24389 else (108/841)*(t-4/29)
    xyz=[inv(fx)*WP[0], inv(fy)*WP[1], inv(fz)*WP[2]]
    rgb=[MI[i][0]*xyz[0]+MI[i][1]*xyz[1]+MI[i][2]*xyz[2] for i in range(3)]
    return tuple(_l2s(c) for c in rgb)
def lum(rgb):
    r,g,b=[_s2l(c) for c in rgb]
    return 0.2126*r+0.7152*g+0.0722*b
def ratio(a,b):
    la,lb=lum(a),lum(b); hi,lo=max(la,lb),min(la,lb)
    return (hi+0.05)/(lo+0.05)

# ---------- build a perceptually even ramp through an anchor ----------
STEPS=[50,100,200,300,400,500,600,700,800,900]
TARGET_L={50:96,100:91,200:83,300:74,400:65,500:56,600:47,700:38,800:29,900:20}

def ramp(anchor_hex, name, anchor_step=500):
    L,a,b = rgb2lab(unhex(anchor_hex))
    # keep the anchor's hue+chroma direction, walk lightness
    out={}
    for s in STEPS:
        tl=TARGET_L[s]
        # scale chroma slightly down at the extremes so it stays in gamut
        k = 1.0 - 0.55*abs(tl-L)/100.0
        rgb=lab2rgb((tl, a*k, b*k))
        out[s]=hx(rgb)
    out[anchor_step]=anchor_hex.upper()   # pin the true brand value
    return out

BG={'base':'#121212','surface':'#1C1C1E','elevated':'#2C2C2E'}

def report(name, r):
    print(f"\n{'='*74}\n{name.upper()} RAMP  (anchor pinned at 500)\n{'='*74}")
    print(f"{'step':<6}{'hex':<10}{'L*':>6}   " + "".join(f"{k:>11}" for k in BG))
    for s in STEPS:
        h=r[s]; L=rgb2lab(unhex(h))[0]
        row=f"{s:<6}{h:<10}{L:>6.1f}   "
        for bn,bv in BG.items():
            cr=ratio(unhex(h),unhex(bv))
            mark='+' if cr>=4.5 else ('~' if cr>=3.0 else '-')
            row+=f"{cr:>9.2f}{mark} "
        print(row)

RAMPS={
 'coral': ramp('#E06665','coral'),
 'blue':  ramp('#007AFF','blue'),
 'green': ramp('#34C759','green'),
 'amber': ramp('#FF9F0A','amber'),
 'red':   ramp('#FF453A','red'),
}
for n,r in RAMPS.items(): report(n,r)
print("\nlegend:  + passes AA 4.5:1 (normal text)   ~ passes 3:1 (large text / UI)   - fails")
json.dump(RAMPS, open('ramps.json','w'), indent=1)
print("\nwrote ramps.json")
