var situations;
var website_ready = false;
var NUM_CHOICES = 2;
var DEBUG = false;
var started = false;
var currentSituation = 0;
var ruleChosen = 0;
var situationCount;

var menuText = 
  "<b>Overview</b><br>Welcome to Choices. This is a simple choice simulator built by me, Michael Ward, "+ 
  "a Senior at the Missouri University of Science and Technology " +
  "as my creative project for Business Ethics: Philosphy 3235. The purpose of this simulator is to present and " +
  "examine six example scenarios that different people may face over the course of their careers. For each scenario, you will be presented with "+
  "two choices. These choices are meant to be representative of a possible action you believe the person in the scenario should do. The choices "+
  "are meant to be split between one that a rule utilitarian would choose and one that an act utilitarian would choose.<br><br>"+
  "Fair warning: some of the scenarios or choices presented may seem outlandish or absurd. This is partially for comedic effect, but also "+
  "to maybe examine some ideas taken to the extreme. So sit back, enjoy, and see which side of the utilitarian split you're on!<br><br><b>Instructions</b><br>"+
  "Nothing too difficult to explain here. Click the button over on the right to begin. After that, the scenario is displayed at the top of the screen. "+
  "From there, make your decision by clicking on one of the buttons below the scenario. A short examination of the choice will be displayed for your "+
  "reading pleasure, and then you can continue to the next scenario by pressing the button on the right. At the end of the game, your leaning towards "+
  "either act or rule utilitarianism will be declared.<br><br>Take your time, think about the consequences of your actions, and have fun playing!<br><br><a href=\"http://www.differencebetween.net/miscellaneous/difference-between-act-utilitarianism-and-rule-utilitarianism/\">Click here for a decent explanation on rule vs act utilitarianism</a>"


let getSituations = async function() {
  var x = await $.getJSON("scenarios.json", function(json) {
    // console.log(json);
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

window.onload = function() 
{
  gotoMenu();
  getSituationsAsync();
}

function setTopText (t) 
{
  $("#top").find(".textHolder").html(t)
}

function toggleButtons() {
  $("#decisions").toggle();
  $("#menu").toggle();
}

function gameOver() 
{
  $(".left").css('width', '75%');
  $(".right").css('width', '25%');
  setTopText("Thanks for playing! I hope that at the very least this small simulation has given you something to consider. The number of choices you made for Rule or Act Utilitarianism are displayed below.")
  $("#menu").hide();
  $("#decisions").hide();
  $("#endgame").show();
  $("#innerbar").css('width', 100*ruleChosen/situationCount + "%")
  $("#actStat").html("Act Utilitarianism: " + (situationCount-ruleChosen));
  $("#ruleStat").html("Rule Utilitarianism: " + ruleChosen);
}

function showSituation(n) 
{
  var sc = getSituation(n);
  setTopText(sc.title);
  for (i = 0; i < NUM_CHOICES; i++)
    $("#choice" + i).find(".textHolder").html(sc.choices[i]);
}

function start() {
  $(".left").css('width', '50%');
  $(".right").css('width', '50%');
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