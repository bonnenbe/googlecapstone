var app = angular.module('module1',['ngRoute', 'ngGrid', 'ui.bootstrap']);


// This filter allows the date time to be displayed properly in the grid.
app.filter('datetime', function() {
    return function(iso186) {
	var newdate = new Date(iso186);
	var datestring = newdate.toDateString().substring(3) + ', ' + newdate.toTimeString().substring(0,5);
	return datestring;
    }
});

//
// Controller
//
app.controller('main', function($http, $scope){
    $http.get('/user').success(function(data){
	$scope.user = data.user;
    })});

function CollapseDemoCtrl($scope) {
    $scope.isCollapsed = false;
}

