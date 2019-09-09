import json
import requests

def fetch_commanders():
  u = 'https://api.scryfall.com/cards/search?q=t%3Alegend+t%3Acreature+f%3Ac+usd%3C5'
  l = list()
  while True:
    resp = requests.get(u)
    if resp.status_code != 200:
      raise(Exception("error"))
    JSON = resp.json()
    cList = JSON['data']
    for card in cList:
      l.append(card['name'])
    if JSON['has_more']:
      u = JSON['next_page']
    else:
      break
  return l

def saveJSONList(l):
  d = {'commanders':l}
  with open('commander-list.json','w') as fout:
    json.dump(d,fout)






commanderList = fetch_commanders()
saveJSONList(commanderList)
  