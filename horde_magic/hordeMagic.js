function play(which) {
  console.log(which);
  if (which == "non-token")
  {
    if (g_decklist.length)
      addCard(g_decklist.pop());
    else
      alert("You win!");
  }
  else
  {
    if (rollDice(11) == 1)
    {
      addCard("Gurmag Angler")
    }
    else
    {
      addCard("Walking Corpse")
    }
  }
}

function shuffleDeck () {
  console.log(g_decklist)
  shuffle(g_decklist);
  console.log(g_decklist)
}

window.onload = function () {
  // set globals
  g_graveyard = [];
  g_decklist = [
    "Anthem of Rakdos",
    "Army of the Damned",
    "Bad Moon",
    "Bottomless Pit",
    "Call to the Grave",
    "Cemetery Reaper",
    "Curse of Disturbance",
    "Delirium Skeins",
    "Destructive Flow",
    "Diregraf Captain",
    "Diregraf Captain",
    "Diregraf Colossus",
    "Dread Slaver",
    "Endless Ranks of the Dead",
    "Fleshbag Marauder",
    "Forsaken Wastes",
    "Geralf's Messenger",
    "Ghoultree",
    "Graf Harvest",
    "Grave Betrayal",
    "Grave Titan",
    "Grixis Slavedriver",
    "In Garruk's Wake",
    "In Oketra's Name",
    "Infectious Horror",
    "Liliana's Mastery",
    "Liliana's Reaver",
    "Living Death",
    "Lord of the Accursed",
    "Maalfeld Twins",
    "Mnemonic Nexus",
    "Necromantic Selection",
    "Noxious Ghoul",
    "Painful Quandary",
    "Plague Wind",
    "Rise of the Dark Realms",
    "Ruination",
    "Shambling Attendants",
    "Sibsig Icebreakers",
    "Siren of the Silent Song",
    "Smallpox",
    "Soulless One",
    "Syphon Flesh",
    "Tresserhorn Skyknight",
    "Unbreathing Horde",
    "Undead Alchemist",
    "Undead Warchief",
    "Vengeful Dead",
    "Vulturous Zombie",
    "Zombie Apocalypse" 
  ]
  shuffle(g_decklist);
}

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function rollDice(n) {
  x = Math.floor(Math.random() * n)+1
  setMsg(x);
  return x;
}

function setMsg(msg) {
  $("#messageBox").text("You rolled a " + String(msg));
}

function addCard (cardName) {
  newDiv = $('<div>',{class:'cardHolder',onclick:"remCard(this)"})
  cardInfo = $.get(
    "http://api.scryfall.com/cards/named",
    {"exact" : cardName},
    function(data) {
    _src = data.image_uris.normal;
    console.log(_src);  
    _class = "card"
    newDiv.prepend($('<img>',{src:_src,class:_class}));
    $('#field').append(newDiv);
    }
  );
}

function remCard (_div)
{
  $(".cardHolder")[0].children[0].src
  _div.parentNode.removeChild(_div);
}