function gameOver()
{
  u = "https://api.scryfall.com/cards/search?q=t%3Alegend+t%3Acreature+f%3Ac+usd%3C5";
  // u = "https://api.scryfall.com/cards/search?q=t%3Alegend+t%3Acreature+f%3Ac+usd<10+id%3D5+r%3Ar";
  $.getJSON(u, function(result) {
    cList = result.data;
    console.log(cList);
    $("#imgs").empty();
    for(i = 0; i < 3; i++) {
      q = Math.floor(Math.random() * cList.length);
      card = cList[q];
      console.log(card)
      cList.splice(q,1);
      $("#imgs").append("<a href=\"" + card.scryfall_uri + "\"><img src= \"" + card.image_uris.normal + "\"/></a>");
      // $("#imgs").append(card.image_uris.normal);
      $("#imgs").append("<br>");
    }
  });
}