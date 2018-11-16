var situations;
var website_ready = false;
var NUM_CHOICES = 2;
var DEBUG = true;
var started = false;
var currentSituation = 0;
var ruleChosen = 0;
var situationCount;

var menuText = "Welcome to Choices. This is a simple choice simulator built by me, Michael Ward, a Senior at the Missouri University of Science and Technology as my creative project for Business Ethics: Philosphy 3235";


let getSituations = async function() {
  var x = await $.getJSON("scenarios.json", function(json) {
    // console.log(json); // this will show the info it in firebug console
  });
  situations = x;
}

function getSituation(sNum) {
  return situations.all[sNum];
}

let getSituationsAsync = async () => {
  await getSituations();
  situationCount = situations.all.length;
  console.log("JSON finished loading: website ready");
  website_ready = true;
}

function gotoMenu()
{
  started = false;
  currentSituation = 0;
  ruleChosen = 0;
  $("#decisions").hide();
  $("#endgame").hide();
  $("#menu").show();
  $("#narrative").html(menuText);
  if (!DEBUG)
    $("#top").html("<div id = \"topText\"><div class=\"textHolder\"></div></div>")
  setTopText("Choices<br>By Michael Ward<br>Philosophy 3235: Business Ethics Creative Project<br>Missouri University of Science and Technology");
}

window.onload = function() {
  gotoMenu();
  getSituationsAsync();
}

function setTopText (t) {
  $("#top").find(".textHolder").html(t)
}

function toggleButtons() {
  $("#decisions").toggle();
  $("#menu").toggle();
}

function gameOver() 
{
  $("#menu").hide();
  $("#decisions").hide();
  $("#endgame").show();
  $("#innerbar").css('width', 100*ruleChosen/situationCount + "%")
}

function showSituation(n) 
{
  console.log("here: " + n);
  var sc = getSituation(n);
  setTopText(sc.title);
  for (i = 0; i < NUM_CHOICES; i++)
    $("#choice" + i).find(".textHolder").html(sc.choices[i]);
}

function start() {
  nextSituation();
  started = true;
}

function onward() {
  if (!started) 
    start()
  else if (currentSituation < situations.all.length)
    nextSituation();
  else
    gameOver();
}

function nextSituation() {
  toggleButtons();
  showSituation(currentSituation);
}

function gotoExplanation(chosen) {

  var sc = getSituation(currentSituation)
  ruleChosen += sc.ruleUtil[chosen]
  $("#narrative").html(sc.exp[chosen]);
  $("#continue").html("Click here to continue.");
  toggleButtons();

  currentSituation++;
}