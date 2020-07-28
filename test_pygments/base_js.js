tables_entries = document.getElementsByClassName("table_entry");
for(i = 0; i < tables_entries.length; i++) {
	// tables_entries[i].style.backgroundColor = "red";
	tables_entries[i].onmouseover = function() {this.style.backgroundColor = "red"};
	tables_entries[i].onmouseout = function() {this.style.backgroundColor = "black"};
}

function mouseOver(element) {
  element.target.style.backgroundColor = "red";
}

function mouseOut(element) {
  element.target.style.backgroundColor = "black";
}