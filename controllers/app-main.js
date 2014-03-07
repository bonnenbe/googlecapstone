var app = angular.module('module1',['ngRoute', 'ngGrid', 'ui.bootstrap']);


//
// Main Controller
//
app.controller('main', function($http, $scope){
    $http.get('/user').success(function(data){
	$scope.user = data.user;
    });
    $scope.today = new Date();
});



app.config(function ($routeProvider) {
    $routeProvider
	.when('/id=:id',
	      {
		  controller: 'updateController',
		  templateUrl: '/views/update.html',
		  controllerAs: 'ctrl'
	      })
	.when('/',
	      {
		  controller: 'listController',
		  templateUrl: '/views/list.html',
		  controllerAs: 'list'
	      })
	.when('/Create',
	      {
		  controller: 'createController',
		  templateUrl: '/views/create.html',
		  controllerAs: 'ctrl'
	      })
	.when('/groups',
	      {
		  controller: 'groupController',
		  templateUrl: '/views/groups.html',
		  controllerAs: 'ctrl'
	      })
	.otherwise({ redirectTo: '/' });
});


    
