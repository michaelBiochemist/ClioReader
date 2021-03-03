
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
