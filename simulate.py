import json,statistics as S,csv,time
from collections import defaultdict
ACCT=300.0; PS=0.10
FEE={'binance':0.0005,'bitget':0.0006}
def daily_returns(cum):
    out=[];prev=0.0
    for v in cum:
        out.append((1+v/100)/(1+prev/100)-1); prev=v
    return out
def sim(rets,scale,cost_per_day,trade_caps,slip_bps,fee,turn):
    eq=ACCT;hwm=ACCT;peak=ACCT;mdd=0;flags=set();wk_start=eq;weekly=[];wk_ps_base=eq
    for i,r in enumerate(rets):
        r=r*scale + trade_caps[i]
        r-= turn[i]*scale*2*(fee+slip_bps/1e4)
        if r< -0.10: r=-0.10; flags.add('daily10')
        eq*=1+r
        if i%7==6:
            if eq>hwm: eq-=PS*(eq-hwm); hwm=eq
            w=eq/wk_start-1; weekly.append(w); wk_start=eq
            if w<=-0.15: flags.add('weekly15'); break
        peak=max(peak,eq); mdd=max(mdd,1-eq/peak)
        if eq<=ACCT*0.90: flags.add('leader10');
        if 'leader10' in flags:
            weekly.append(eq/wk_start-1) if i%7!=6 else None; break
    return eq,weekly,mdd,flags
rows=[]

raw=json.load(open('bn_raw.json')); pos=json.load(open('bn_positions.json'))
for pid,d in raw.items():
    ch=d['chart']['ROI'];
    if not ch or len(ch)<85: continue
    days=[c['dateTime'] for c in ch]; rets=daily_returns([c['value'] for c in ch])
    mb=float(d['detail']['marginBalance']); P=pos.get(pid,[])
    levs=sorted(float(p['leverage']) for p in P if p.get('leverage'))
    medlev=S.median(levs) if levs else None
    turn=[0.0]*len(days); caps=[0.0]*len(days)
    for p in P:
        k=max(j for j,t in enumerate(days) if t<=p['closed']) if p['closed']>=days[0] else None
        if k is None: continue
        turn[k]+=p['closedVolume']*(p['avgCost']+p['avgClosePrice'])/2/mb
        loss=p['closingPnl']/mb
        caps[k]+=0
        p['_k']=k
    for name,scale in [('2x',min(1,2/medlev) if medlev else 1),('actual',1.0)]:
        cp=[0.0]*len(days)
        for p in P:
            if '_k' in p:
                l=p['closingPnl']/mb*scale
                if l<-0.05: cp[p['_k']]+=(-0.05-l)
        for slip in (5,10,25):
            eq,wk,mdd,fl=sim(rets,scale,0,cp,slip,FEE['binance'],turn)
            rows.append(dict(exchange='Binance',leader=d['list']['nickname'],id=pid,url=f"https://www.binance.com/en/copy-trading/lead-details/{pid}",
              lev_med=medlev,scale=name,slip_bps=slip,days=len(rets),trades90=len(P),final=round(eq,2),
              wk_mean=round(S.mean(wk)*100,2) if wk else None,wk_median=round(S.median(wk)*100,2) if wk else None,
              mdd=round(mdd*100,2),stops=';'.join(sorted(fl)) or 'none',leader_mdd_listed=round(d['list']['mdd'],2)))

bg=json.load(open('bg_raw.json'))
cands=[]
for u,d in bg.items():
    st=d['stats'];roi=d['roi']
    try: mr=float(st['maxRetracement']); pr=float(st['profitRate']); fp=float(st['totalFollowProfit'])
    except: continue
    if len(roi)<85 or float(roi[0]['amount'])==0 or not(mr<15 and 0<pr<300 and fp>0): continue
    cands.append((mr,u))
for mr,u in sorted(cands)[:8]:
    d=bg[u];st=d['stats'];rets=daily_returns([float(x['amount']) for x in d['roi']])
    ntr=(st.get('profitTrades') or 0)+(st.get('lossTrades') or 0)
    turn=[ntr/len(rets)]*len(rets)
    ps=float(st.get('distributeRatio') or 0)
    for slip in (5,10,25):
        eq,wk,mdd,fl=sim(rets,1.0,0,[0]*len(rets),slip,FEE['bitget'],turn)
        rows.append(dict(exchange='Bitget',leader=d['list']['traderNickName'],id=u,url=f"https://www.bitget.com/copy-trading/trader/{u}/futures",
          lev_med=None,scale='unknown(1x of leader)',slip_bps=slip,days=len(rets),trades90=ntr,final=round(eq,2),
          wk_mean=round(S.mean(wk)*100,2) if wk else None,wk_median=round(S.median(wk)*100,2) if wk else None,
          mdd=round(mdd*100,2),stops=';'.join(sorted(fl)) or 'none',leader_mdd_listed=mr))
with open('results.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for r in rows:
    if r['slip_bps']==10: print(r['exchange'],r['leader'][:14],r['lev_med'],r['scale'][:6],r['trades90'],r['final'],r['wk_mean'],r['wk_median'],r['mdd'],r['stops'])
