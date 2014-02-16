var app = angular.module('module1',['ngRoute', 'ngGrid', 'ui.bootstrap']);


// This filter allows the date time to be displayed properly in the grid.
app.filter('datetime', function() {
    return function(iso186) {
	newdate = new Date(iso186);
	datestring = newdate.toDateString().substring(3) + ', ' + newdate.toTimeString().substring(0,5);
	return datestring;
    }
});

//
// Controllers
//
app.controller('main', function($http, $scope){
    $http.get('/user').success(function(data){
	$scope.user = data.user;
    })});

// List(main page) Controller
app.controller('listController',['$http', '$scope', '$location', function($http, $scope, $location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.searchableFields = ['technician','priority'];
    $scope.searchField = $scope.searchableFields[0];
    

    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
    };
    $scope.totalServerItems = 0;
    $scope.pagingOptions = {
        pageSizes: [5, 10, 25, 50],
        pageSize: 5,
        currentPage: 1
    };

    // Sets paging data
    $scope.setPagingData = function(pageSize, page, data){
	$scope.crs = data.changerequests;
        if (!$scope.$$phase) {
            $scope.$apply();
        }
    };

    // On get new page
    $scope.getPagedDataAsync = function (pageSize, page, searchParams) {
        setTimeout(function () {
            var params = {};
	    params["offset"] = (page - 1) * pageSize;
	    params["limit"] = pageSize;
	    for (var attr in searchParams) {params[attr] = searchParams[attr]};
	    var obj = {};
	    obj["params"] = params;
	    $http.get('/changerequests', obj).success(function (data){
		$scope.setPagingData(pageSize, page, data);
	    });
        }, 100);
    };
    
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, {});
    
    // set paging data when paging data is changed or page is turned	
    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        if (newVal !== oldVal){
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, {});
        }
    }, true);
    $scope.$watch('filterOptions', function (newVal, oldVal) {
        if (newVal !== oldVal) {
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, {});
        }
    }, true);

    $scope.gridOptions = {
        data: 'crs',
	enablePaging: true,
	showFooter: true,
	totalServerItems: 'totalServerItems',
	pagingOptions: $scope.pagingOptions,
	filterOptions: $scope.filterOptions,
	columnDefs: [  	{ field:"created_on | datetime", displayName: "Created On"},
			{ field:"technician", displayName: "Technician"},
	             	{ field:"summary", displayName: "Summary"},
			{ field:"priority", displayName: "Priority"},
			{ field:"startTime | datetime", displayName: "Start Time"},
			{ field:"endTime | datetime", displayName: "End Time"},
			{ field:"id", displayName: "ID", cellTemplate: '<div class="ngCellText" ng-class="col.colIndex()"><a ng-href="#/id={{row.getProperty(col.field)}}">{{row.getProperty(col.field)}}</a></div>'}
//			{ field:"", displayName: "delete", cellTemplate:'<div class="ngCellText"><a ng-href ng-click="ctrl.remove(1)">[X]</a></div>'}
]
    };




    this.remove = function remove(index){
	    alert(index);
	$http.delete('/changerequests/' + $scope.crs[index].id,"").success(function() {
	    $scope.crs.splice(index,1);
	})};
    this.search = function search(){
	var searchParams = {};
	if ($scope.searchText.length > 0)	    
	    searchParams[$scope.searchField] = $scope.searchText;
	$scope.pagingOptions.currentPage = 1;
	$scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, searchParams);
    };
}]);

app.controller('createController', function($http,$scope,$location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.cr = {};
    $scope.cr.technician = $scope.user;
    
    this.add = function add(cr){
	newcr = new Object();
	angular.copy(cr,newcr);
	newcr.startTime = new Date(cr.startDate.getFullYear(),cr.startDate.getMonth(),cr.startDate.getDate(),
				   cr.startTime.getHours(),cr.startTime.getMinutes(),cr.startTime.getSeconds());
	delete newcr.startDate;
	newcr.endTime = new Date(cr.endDate.getFullYear(),cr.endDate.getMonth(),cr.endDate.getDate(),
				   cr.endTime.getHours(),cr.endTime.getMinutes(),cr.endTime.getSeconds());
	delete newcr.endDate;
	
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
app.controller('DateCtrl', function($scope){
    $scope.format = 'dd-MMMM-yyyy';
    $scope.dateOptions = {};
    $scope.open = function($event) {
	$event.preventDefault();
	$event.stopPropagation();
	$scope.opened = true;
    };
});
	
app.controller('TimeCtrl', function($scope){
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

