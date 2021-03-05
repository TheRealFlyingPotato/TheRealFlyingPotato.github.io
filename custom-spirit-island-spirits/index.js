var spirit_names = [
  "Magma Flows from the Mountains",
  "The Island's Ever Changing Heart"
]
window.onload = function() {
  container = $("#spirit-container").first();
  spirit_names.forEach((n) => {
    name_uri = n.replaceAll(' ','-').replaceAll("'","").toLowerCase();
    var path = "custom-spirits/" + name_uri + "/";
    var spirit = $("<div class='spirit'></div>");
    spirit.append("<h3>"+n+"</h3>");
    spirit.append("<a href='"+path+"board.html'>Board</a><br/>");
    spirit.append("<a href='"+path+"cards.html'>Cards</a>");
    container.append(spirit);
  })
};