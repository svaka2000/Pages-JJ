import json
exec(open('ramp.py').read().split('# ---------- build')[0])
d=json.load(open('tokens.json')); sem=d['semantic']
def solve_bg_for(fg_hex, anchor_hex, target=4.6):
    L,a,b=rgb2lab(unhex(anchor_hex)); f=unhex(fg_hex)
    tl=30.0
    best=None
    while tl>=8.0:
        c=lab2rgb((tl,a*0.30,b*0.30))
        if ratio(f,c)>=target: best=hx(c)
        tl-=0.5
    # walk down until it passes, take the LIGHTEST that passes
    tl=30.0
    while tl>=8.0:
        c=lab2rgb((tl,a*0.30,b*0.30))
        if ratio(f,c)>=target: return hx(c)
        tl-=0.5
    return best
print(f"{'token':<10}{'fg':<10}{'old bg':<10}{'old':>6}   {'new bg':<10}{'new':>6}  status")
print("-"*66)
for n,v in sem.items():
    old=v['bg']; oldr=ratio(unhex(v['fg']),unhex(old))
    nb=solve_bg_for(v['fg'],v['anchor'])
    nr=ratio(unhex(v['fg']),unhex(nb))
    v['bg']=nb
    print(f"{n:<10}{v['fg']:<10}{old:<10}{oldr:>6.2f}   {nb:<10}{nr:>6.2f}  {'PASS' if nr>=4.5 else 'FAIL'}")
    # also verify the tint itself is distinguishable from page bg
    v['bg_vs_base']=round(ratio(unhex(nb),unhex('#121212')),2)
print("\ntint vs page background #121212 (want >1.1 so the tint is visible):")
for n,v in sem.items(): print(f"  {n:<10}{v['bg']}  {v['bg_vs_base']}")
d['semantic']=sem; json.dump(d,open('tokens.json','w'),indent=1)
print("\nFINAL SEMANTIC TOKENS")
print(json.dumps(sem,indent=1))
