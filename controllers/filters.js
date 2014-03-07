// This filter allows the date time to be displayed properly in the grid.
app.filter('datetime', function() {
    return function(iso186) {
	var newdate = new Date(iso186);
	var datestring = newdate.toDateString().substring(3) + ', ' + newdate.toTimeString().substring(0,5);
	return datestring;
    }
});

// returns the timezone portion of a datestring, given an isoformat datestring
app.filter('timezone', function() {
    return function(iso) {
	var date = new Date(iso);
	var datestring = date.toString();
	return "UTC" + datestring.substring(datestring.indexOf("GMT")+3);
    }
});