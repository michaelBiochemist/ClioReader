
var today = new Date();
var hour = today.getHours();
if (hour < 5 || hour > 18) {
	var time = "evening";
}
else if(hour < 12) {
	var time = "morning";
}
else {
	var time = "afternoon";
}
document.getElementById('time').innerHTML = time;

var navbar = "<h1><div class = \"nav-wrapper\"><nav class = \"nav-menu\"> <ul class = \"main-menu\"> <li> <a href=\" index.html\"> Home </a> </li> <li> <a href=\"#projects\"> Projects </a>  <ul class = \"sub-menu\"> <li><a href=#books>Book Reviews</a></li><br></ul></li><li> <a href=\"resume.pdf\"> Resume </a> </li> <li> <a href=\"mailto:michael@biochemist.me\">Contact </a></li> <!-- <li><a href=\"#impossible\">Impossible</a></li> --></ul> </nav></div></h1>";
var oldbar = "<h1><div class = \"nav-wrapper\"><nav class = \"nav-menu\"> <ul class = \"main-menu\"> <li> <a href=\" index.html\"> Home </a> </li> <li> <a href=\"#projects\"> Projects </a>  <ul class = \"sub-menu\"> <li><a href=#books>Book Reviews</a></li><br> <li><a href=#soft>Software</a></li><br>  </ul></li><li> <a href=\"resume.pdf\"> Resume </a> </li> <li> <a href=\"mailto:michael@biochemist.me\">Contact </a></li> <!-- <li><a href=\"#impossible\">Impossible</a></li> --></ul> </nav></div></h1>";

document.getElementById('navbar').innerHTML= navbar;
