// jQuery.ajaxPrefilter(function(options) {
//   if (options.crossDomain && jQuery.support.cors) {
//       options.url = 'https://cors-anywhere.herokuapp.com/' + options.url;
//   }
// });

$(document).ready( () => {
  var url = 'https://boardgamegeek.com/collection/user/TheRealFlyingPotato?objecttype=thing&ff=1&subtype=boardgame'
  $.ajax({ url: url, success: function(data) { console.log(data); } });
});