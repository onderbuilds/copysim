import requests,json,time
raw=json.load(open('bn_raw.json'));cut=(time.time()-91*86400)*1000;P={}
for pid in raw:
  L=[];p=1
  while p<=40:
    r=requests.post('https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/position-history',json={"pageNumber":p,"pageSize":50,"portfolioId":pid,"sort":"OPENING"},timeout=20).json()
    lst=(r.get('data') or {}).get('list') or []
    L+=lst
    if not lst or min(x['opened'] for x in lst)<cut: break
    p+=1; time.sleep(0.3)
  P[pid]=[x for x in L if x['closed'] and x['closed']>=cut]
  print(pid,len(P[pid]),p,flush=True)
json.dump(P,open('bn_positions.json','w'))
