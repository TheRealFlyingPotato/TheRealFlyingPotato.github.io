import json
import re
import requests

# def fetchimgdata(s):
#   s = s[2:-2]
#   # print(s)
#   resp = requests.get('https://api.scryfall.com/cards/named?exact="' + s + '"')
#   if resp.status_code == 200:
#     cardData = resp.json()
#   else:
#     print("oof")
#     raise(Exception("error on {}\n".format(s)))
#   return cardData["image_uris"]["normal"],s

with open('template.html', 'r') as fin:
  s = fin.read()
  l = s.split('|body|')
  htmlheader = l[0]
  htmlfooter = l[1]
  htmlbody = ""

with open('games.json') as fin:
  data = json.load(fin)


greytoggle = 0
for key in sorted(data.keys()):
  if key[0] == '_':
    continue
  header = "<h3><a href=\"{}\"> {} </a> </h3>".format(data[key]['url'], key)
  content = data[key]['desc']
  imgs = ''
  # imgsdone = []
  # imgset = set(re.findall(r'\[\[.*?\]\]', content))
  # for img in re.findall(r'\[\[.*?\]\]', content):
    # if img in imgsdone:
      # continue
    # imgsdone.append(img)
    # imgurl, name = fetchimgdata(img)
  for img in data[key]['imgs']:
    imgs += "<div class=\"column\"><img src=\"{}\"></div>".format(img)
    print(img)
    # contentsplit = content.split(img)
    # content = "<b>{}</b>".format(name).join(contentsplit)
  # coloricons = ''
  # for color in data[key]['colors']:
    # coloricons += "<div class=\"iconcolumn\"><img class=\"icon\" src={}></div>".format(data['_mana_urls'][color])
  # print(coloricons)
  htmlbody += "<div class=\"{}\">{}\n{}\n<br> <div class=\"row\">{}</div> </div>\n".format(['d-g','l-g'][greytoggle], header, content, imgs)
  greytoggle = not greytoggle

with open('index.html', 'w') as fout:
  fout.write(htmlheader + htmlbody + htmlfooter)

print("\n\nindex.html written\n")