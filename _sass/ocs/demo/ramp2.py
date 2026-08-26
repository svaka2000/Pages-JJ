import json
exec(open('ramp.py').read().split('# ---------- build')[0])   # reuse color math

STEPS=[50,100,200,300,400,500,600,700,800,900]
TARGET_L={50:96,100:91,200:83,300:74,400:65,500:56,600:47,700:38,800:29,900:20}
BG={'base':'#121212','surface':'#1C1C1E','elevated':'#2C2C2E'}

def natural_step(hexv):
    L=rgb2lab(unhex(hexv))[0]
    return min(STEPS,key=lambda s:abs(TARGET_L[s]-L)), L

def ramp(anchor_hex):
    anchor,L0 = natural_step(anchor_hex)
    L,a,b = rgb2lab(unhex(anchor_hex))
    out={}
    for s in STEPS:
        tl=TARGET_L[s]
        k = 1.0 - 0.55*abs(tl-L)/100.0
        out[s]=hx(lab2rgb((tl,a*k,b*k)))
    out[anchor]=anchor_hex.upper()
    return out, anchor, L0

def mono_check(r):
    Ls=[rgb2lab(unhex(r[s]))[0] for s in STEPS]
    return all(Ls[i]>Ls[i+1] for i in range(len(Ls)-1)), Ls

print("BRAND + NEUTRAL RAMPS (anchor placed at its NATURAL lightness step)\n")
BRAND={'coral':'#E06665'}
NEUTRAL_ANCHOR='#8E8E93'
allr={}
for n,v in list(BRAND.items())+[('neutral',NEUTRAL_ANCHOR)]:
    r,anchor,L0=ramp(v); allr[n]=r
    ok,Ls=mono_check(r)
    print(f"{'='*76}\n{n.upper()}  anchor {v} (L*={L0:.1f}) pinned at step {anchor}   monotonic={ok}\n{'='*76}")
    print(f"{'step':<6}{'hex':<10}{'L*':>6}   " + "".join(f"{k:>11}" for k in BG))
    for s in STEPS:
        h=r[s]; L=rgb2lab(unhex(h))[0]
        row=f"{s:<6}{h:<10}{L:>6.1f}   "
        for bn,bv in BG.items():
            cr=ratio(unhex(h),unhex(bv))
            row+=f"{cr:>9.2f}{'+' if cr>=4.5 else ('~' if cr>=3.0 else '-')} "
        print(row)
    print()

# ---------- semantic triplets: fg (AA on elevated), border (3:1), bg (subtle tint) ----------
def solve_fg(anchor_hex, target=4.6, bg='#2C2C2E'):
    L,a,b=rgb2lab(unhex(anchor_hex)); bgr=unhex(bg)
    tl=L
    while tl<=100:
        c=lab2rgb((tl,a*(1-0.35*abs(tl-L)/100),b*(1-0.35*abs(tl-L)/100)))
        if ratio(c,bgr)>=target: return hx(c)
        tl+=0.5
    return None
def solve_border(anchor_hex, target=3.05, bg='#1C1C1E'):
    L,a,b=rgb2lab(unhex(anchor_hex)); bgr=unhex(bg)
    tl=L
    while tl<=100:
        c=lab2rgb((tl,a,b))
        if ratio(c,bgr)>=target: return hx(c)
        tl+=0.5
    return None
def solve_bg(anchor_hex, L_target=24):
    L,a,b=rgb2lab(unhex(anchor_hex))
    return hx(lab2rgb((L_target,a*0.30,b*0.30)))

SEM={'brand':'#E06665','info':'#007AFF','success':'#34C759','warning':'#FF9F0A','danger':'#FF453A'}
print(f"\n{'='*84}\nSEMANTIC TRIPLETS — each AA-verified for its job\n{'='*84}")
print(f"{'token':<10}{'anchor':<10}{'fg (text)':<12}{'AA/elev':>8}   {'border':<10}{'3:1/surf':>9}   {'bg tint':<10}{'fg-on-bg':>9}")
sem_out={}
for n,v in SEM.items():
    fg=solve_fg(v); bd=solve_border(v); bgt=solve_bg(v)
    r1=ratio(unhex(fg),unhex('#2C2C2E')); r2=ratio(unhex(bd),unhex('#1C1C1E')); r3=ratio(unhex(fg),unhex(bgt))
    sem_out[n]={'anchor':v.upper(),'fg':fg,'border':bd,'bg':bgt}
    print(f"{n:<10}{v:<10}{fg:<12}{r1:>7.2f}{'+' if r1>=4.5 else '-'}   {bd:<10}{r2:>8.2f}{'+' if r2>=3.0 else '-'}   {bgt:<10}{r3:>8.2f}{'+' if r3>=4.5 else '-'}")
json.dump({'ramps':allr,'semantic':sem_out},open('tokens.json','w'),indent=1)
print("\nwrote tokens.json")
