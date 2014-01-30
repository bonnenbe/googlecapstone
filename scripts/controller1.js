var app = angular.module('module1',['ngRoute', 'ngAnimate'])
    .controller('controller1',['$http', '$scope', function($http, $scope){
	$scope.priorities = ['routine', 'sensitive'];
	$http.get('/changerequests',"").success(function(data) {
	    $scope.crs = data.changerequests;
	    window.alert(JSON.stringify($scope.crs));
	});
			
	this.add = function add(cr){
	    newcr = new Object();
	    for(var k in cr) newcr[k]=cr[k];
	    $http.post('/changerequests',JSON.stringify(newcr)).success(function(data) {
		newcr.id = data.id;
		$scope.crs.push(newcr);
	    	console.log("Successful add");
	    }).error(function() {
	    	console.log("Unsuccessful add");
	    });
	};
	this.remove = function remove(index){
	    $http.delete('/changerequests/' + $scope.crs[index].id,"").success(function() {
		$scope.crs.splice(index,1);
	    })};
    }])
    .controller('updateController', ['$http', '$scope', function($routeParams, $http, $scope){
	$http.get('/changerequests/id/' + $routeParams.id,"").success(function(data) {
	    $scope.cr = data.changerequest;
	})
    }]);
	

app.config(function ($routeProvider) {
    $routeProvider
	.when('/id/:id',
	      {
		  controller: 'updateController',
		  templateUrl: '/views/update.html'
	      })
	.when('/',
	      {
		  controller: 'controller1',
		  templateUrl: '/views/view1.html'
	      })
	.otherwise({ redirectTo: '/' });
});

