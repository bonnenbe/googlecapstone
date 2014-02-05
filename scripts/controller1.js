var app = angular.module('module1',['ngRoute', 'ngGrid']);

app.controller('listController',['$http', '$scope', '$location', function($http, $scope, $location){
    $scope.priorities = ['routine', 'sensitive'];
    $http.get('/changerequests',"").success(function(data) {
	$scope.crs = data.changerequests;
    });

    $scope.gridOptions = {
        data: 'crs',
	//                    columnDefs: [{ field:"name", displayName: "Name"},
	//                        { field:"age", displayName: "Age"}]
    };

    this.remove = function remove(index){
	$http.delete('/changerequests/' + $scope.crs[index].id,"").success(function() {
	    $scope.crs.splice(index,1);
	})};
    
}]);

app.controller('createController', function($http,$scope,$location){
    $scope.priorities = ['routine', 'sensitive'];
    
    this.add = function add(cr){
	newcr = new Object();
	angular.copy(cr,newcr);
	$http.post('/changerequests',JSON.stringify(newcr)).success(function(data) {
	    newcr.id = data.id;
	    //$scope.crs.push(newcr);
	    console.log("Successful add");
	    $location.path('#');
	}).error(function() {
	    console.log("Unsuccessful add");
	});
    };    
});

app.controller('updateController', function($routeParams, $http, $scope, $location){
	$scope.priorities = ['routine', 'sensitive'];
	$http.get('/changerequests/' + $routeParams.id,"").success(function(data) {
	    $scope.cr = data.changerequest;
	});
	this.update = function update(cr){
	    $http.put('/changerequests/' + $routeParams.id,JSON.stringify(cr)).success(function(data) {
		$location.path('#');
	    })};
		
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
		  controllerAs: 'ctrl'
	      })
	.when('/Create',
	      {
		  controller: 'createController',
		  templateUrl: '/views/create.html',
		  controllerAs: 'ctrl'
	      })
	.otherwise({ redirectTo: '/' });
});

