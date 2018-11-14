var situations;
var website_ready = false;
var NUM_CHOICES = 4;
var DEBUG = true;
var started = false;
var currentSituation = 0;

let getSituations = async function() {
  var x = await $.getJSON("scenarios.json", function(json) {
    // console.log(json); // this will show the info it in firebug console
  });
  situations = x;
}

function getSituation(sNum) {
  return situations.all[sNum]
}

let getSituationsAsync = async () => {
  await getSituations();

  // var tmp = getSituation(0);
  // console.log("console.log(getSituation(0)) via tmp;")
  // console.log(tmp);
  console.log("JSON finished loading: website ready");
  website_ready = true;
  // console.dir(getSituation(0));
}

window.onload = function() {
  $("#decisions").toggle();
  if (!DEBUG)
    $("#top").html("<div id = \"topText\"><div class=\"textHolder\"></div></div>")
  setTopText("Choices<br>By Michael Ward<br>Philosophy 3235: Business Ethics Creative Project<br>Missouri University of Science and Technology");
  // setTopText("Choices&#13;&#10;By Michael Ward&#13;&#10;Philosophy 3235: Business Ethics Creative Project&#13;&#10;Missouri University of Science and Technology");
  getSituationsAsync();
}

function setTopText (t) {
  $("#top").find(".textHolder").html(t)
}

function toggleButtons() {
  $("#decisions").toggle();
  $("#menu").toggle();
}


function showSituation(n) {
  var sc = getSituation(n);
  setTopText(sc.title);
  // $("#top").html("<div class=\"textHolder\">"+sc.title+"</div>")
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
    console.log("No more situations!");
}

function nextSituation() {
  toggleButtons();
  showSituation(currentSituation);
}

function gotoExplanation(chosen) {

  var sc = getSituation(currentSituation)
  // console.dir(currentSituation);
  // console.dir(chosen)
  // console.dir(sc.exp[chosen]);
  $("#narrative").html(sc.exp[chosen]);
  $("#continue").html("Click here to continue.");
  toggleButtons();

  currentSituation++;
}