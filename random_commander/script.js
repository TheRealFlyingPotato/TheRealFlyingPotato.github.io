function gameOver()
{
  var namelog = []
  var min = '0';
  var max = '.79';
  var coloridentity = 'WUBRG';
  var ciOperator = ':';
  
  if ($("#mincost")[0].value != "")
    min = $("#mincost")[0].value;
  if ($("#maxcost")[0].value != "")
    max = $("#maxcost")[0].value;
  if ($("#ci")[0].value != "")
    coloridentity = $("#ci")[0].value;
  if ($("#exactCI")[0].checked)
    ciOperator = "=";


  console.log(min)
  console.log(max)
  console.log(coloridentity)
  console.log(ciOperator)
  u = "https://api.scryfall.com/cards/random?q=is:commander usd<" + max + "usd>" + min + "ci" + ciOperator + coloridentity;
  console.log(u)
  $("#imgs").empty();
  for(i = 0; i < 3; i++) {
    $.getJSON(u, function(result) {
      if (!namelog.includes(result.name))
      {
        // console.log(result);
        try
        {
          $("#imgs").append("<a href=\"" + result.scryfall_uri + "\"><img src= \"" + result.image_uris.normal + "\"/></a>");
          $("#imgs").append("<br>");
          namelog.push(result.name)
        }
        catch(err)
        {
          console.log("ERROR on: " + result.scryfall_uri)
          i--
        }
      }
    });
  }
}