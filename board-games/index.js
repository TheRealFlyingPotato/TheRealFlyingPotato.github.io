jQuery.ajaxPrefilter(function(options) {
  if (options.crossDomain && jQuery.support.cors) {
    options.url = 'https://cors-anywhere.herokuapp.com/' + options.url;
    // options.url = 'https://pacific-reaches-88708.herokuapp.com/' + options.url;
  }
});

$(document).ready( () => {
  var logs = ['0.1: Added heroku for cors-anywhere'];
  l = 'changelog:\n';
  for (const x of logs) { l = l + '\n' + x};
  console.log(l);
  var url = 'https://boardgamegeek.com/collection/user/TheRealFlyingPotato?objecttype=thing&ff=1&subtype=boardgame'
  $.ajax({ url: url, success: function(data) { console.log(data); } });
});