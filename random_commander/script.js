function gameOver()
{
  u = "https://api.scryfall.com/cards/search?q=t%3Alegend+t%3Acreature+f%3Ac+usd%3C10";
  u = "https://api.scryfall.com/cards/search?q=t%3Alegend+t%3Acreature+f%3Ac+usd<10+id%3D5+r%3Ar";
  $.getJSON(u, function(result) {
    cList = result.data;
    console.log(cList);
    for(i = 0; i < cList.length; i++) {
      console.log(cList[i].name)
      console.log(cList[i].image_uris.normal)
    }
  });
}