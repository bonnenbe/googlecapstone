var app = angular.module('module1',['ngRoute', 'ngGrid'])
    .controller('listController',['$http', '$scope', function($http, $scope){
	$scope.priorities = ['routine', 'sensitive'];
	$http.get('/changerequests',"").success(function(data) {
	    $scope.crs = data.changerequests;
	});

	$scope.myData = [{name: "Moroni", age: 50},
                 {name: "Tiancum", age: 43},
                 {name: "Jacob", age: 27},
                 {name: "Nephi", age: 29},
                 {name: "Enos", age: 34}];
	$scope.gridOptions = {data: 'myData',
			      columnDefs: [{ field:"name", displayName: "Name"},
					   { field:"age", displayName: "Age"}] };
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
    .controller('updateController', function($routeParams, $http, $scope, $location){
	$scope.priorities = ['routine', 'sensitive'];
	$http.get('/changerequests/' + $routeParams.id,"").success(function(data) {
	    $scope.cr = data.changerequest;
	});
	this.update = function update(cr){
	    newcr = new Object();
	    for(var k in cr) newcr[k]=cr[k];
	    $http.put('/changerequests/' + $routeParams.id,JSON.stringify(newcr)).success(function() {
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
		  templateUrl: '/views/view1.html',
		  controllerAs: 'ctrl'
	      })
	.otherwise({ redirectTo: '/' });
});

