import requests,json,time
rows=[]
for p in range(1,9):
  r=requests.post('https://www.bitget.com/v1/trigger/trace/public/traderList',json={"pageNo":p,"pageSize":20,"sortRule":1,"model":1,"languageType":0},timeout=20).json()
  rows+=r['data']['rows']; time.sleep(0.3)
json.dump(rows,open('bg_list.json','w'))
out={}
for x in rows:
  u=x['traderUid']
  try:
    d=requests.post('https://www.bitget.com/v1/trigger/trace/public/cycleData',json={"languageType":0,"triggerUserId":u,"cycleTime":90},timeout=20).json()['data']
  except Exception as e: print(u,e); continue
  st=d['statisticsDTO']; roi=d['roiRows']['rows']
  out[u]={'list':x,'stats':st,'roi':roi}
  print(u,x['traderNickName'][:15],st.get('maxRetracement'),st.get('profitRate'),st.get('totalFollowProfit'),st.get('distributeRatio'),roi[0]['amount'] if roi else None,flush=True)
  time.sleep(0.3)
json.dump(out,open('bg_raw.json','w'))
