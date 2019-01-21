// Move between pages with left/right arrow keys
document.onkeyup = function(e) {
  if(e.keyCode == 39) {
    a = document.getElementById('next_page');
    if (typeof a != 'undefined') {
    	window.location = a.href;
    }
  } else if (e.keyCode == 37) {
  	a = document.getElementById('prev_page');
    if (typeof a != 'undefined') {
    	window.location = a.href;
    }
  }
}
