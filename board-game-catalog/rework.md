DO NOT modify boardgames.json during this.

each boardgame in the json loaded may have a "hide" key. If that is 1, don't display the game at all UNLESS a special url param is used. You decide what that looks like

the whole boardgame-catalog index needs reformatting:
1. get rid of the header at the top
2. the search filters section should now toggle open when a small "hovering" (top left of screen, stays there while scrolling) button ">" is pressed. The filters section should also stay there while the page is scrolling, with a "<" button to rehide it.

The game cards are too hefty. Much less margin between them, they should bascially be square "tiles"

I don't want the "card body" for each section anymore, so it's just an image.

Clicking on a game should link to the url of the game. That will be a new key in the json as well, to be edited later - just "bggurl"