var spirit_names = [
  "Magma Flows from the Mountains",
  "The Island's Ever Changing Heart"
]
window.onload = function() {
  container = $("#spirit-container").first();
  spirit_names.forEach((n) => {
    name_uri = n.replaceAll(' ','-').replaceAll("'","").toLowerCase();
    var path = "custom-spirits/" + name_uri + "/";
    var spirit = $("<a href=\"#\" class=\"list-group-item list-group-item-action flex-column align-items-start\" style=\"background-image:linear-gradient(rgba(0, 0, 0, 0.25),rgba(0, 0, 0, 0.25)),url("+path+"bg.png);background-position:center\">");
    spirit.append("<h4>"+n+"</h4>");
    // spirit.append("<ul>")
    // btn_class = 'btn btn-danger btn-sm'
    btn_class="btn"
    spirit.append("<a class='"+btn_class+"' href='"+path+"board.html'>Board</a>");
    spirit.append("<a class='"+btn_class+"' href='"+path+"cards.html'>Cards</a>");
    container.append(spirit);
  })
};