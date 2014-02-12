var app = angular.module('module1',['ngRoute', 'ngGrid', 'ui.bootstrap']);

app.filter('datetime', function() {
    return function(iso186) {
	newdate = new Date(iso186);
	datestring = newdate.toDateString().substring(3) + ', ' + newdate.toTimeString().substring(0,5);
	return datestring;
    }
});

app.controller('main', function($http, $scope){
    $http.get('/user').success(function(data){
	$scope.user = data.user;
    })});
app.controller('listController',['$http', '$scope', '$location', function($http, $scope, $location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.searchableFields = ['technician','priority'];
    $scope.searchField = $scope.searchableFields[0];
    $http.get('/changerequests',"").success(function(data) {
	$scope.crs = data.changerequests;
    });

    $scope.gridOptions = {
        data: 'crs',
	columnDefs: [  	{ field:"created_on | datetime", displayName: "Created On"},
			{ field:"technician", displayName: "Technician"},
	             	{ field:"summary", displayName: "Summary"},
			{ field:"priority", displayName: "Priority"},
			{ field:"id", displayName: "ID", cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><a ng-href="#/id={{row.getProperty(col.field)}}">{{row.getProperty(col.field)}}</a></div>'}]
    };

    this.remove = function remove(index){
	$http.delete('/changerequests/' + $scope.crs[index].id,"").success(function() {
	    $scope.crs.splice(index,1);
	})};
    this.search = function search(){
	var obj = {};
	obj["params"] = {};
	if ($scope.searchText.length > 0)	    
	    obj.params[$scope.searchField] = $scope.searchText;
	$http.get('/changerequests',obj).success(function(data) {
	    $scope.crs = data.changerequests;
	})};
}]);

app.controller('createController', function($http,$scope,$location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.cr = {};
    $scope.cr.technician = $scope.user;
    
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
	
function CollapseDemoCtrl($scope) {
    $scope.isCollapsed = false;
}

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

