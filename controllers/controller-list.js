// This filter allows the date time to be displayed properly in the grid.
app.filter('datetime', function() {
    return function(iso186) {
	var newdate = new Date(iso186);
	var datestring = newdate.toDateString().substring(3) + ', ' + newdate.toTimeString().substring(0,5);
	return datestring;
    }
});

// List(main page) Controller
app.controller('listController',['$http', '$scope', '$location', function($http, $scope, $location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.searchableFields = ['technician','priority'];
    $scope.searchParams = {field: $scope.searchableFields[0],
			   text: ""};

    $scope.filterOptions = {
        filterText: "",
        useExternalFilter: true
    };
    $scope.totalServerItems = 0;
    $scope.pagingOptions = {
        pageSizes: [5, 10, 25, 50],
        pageSize: 5,
        currentPage: 1,
	totalServerItems: false
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
	    if (searchParams.text)
		params[searchParams.field] = searchParams.text;
	    var obj = {};
	    obj["params"] = params;
	    $http.get('/changerequests', obj).success(function (data){
		$scope.setPagingData(pageSize, page, data);
	    });
        }, 100);
    };


    
    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.searchParams);
    
    // set paging data when paging data is changed or page is turned	
    $scope.$watch('pagingOptions', function (newVal, oldVal) {
        if (newVal !== oldVal) {
          $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.searchParams);
        }
    }, true);
    $scope.$watch('filterOptions', function (newVal, oldVal) {
        if (newVal !== oldVal) {
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.searchParams);
        }
    }, true);

    $scope.gridOptions = {
        data: 'crs',
	enablePaging: true,
	showFooter: true,
	footerTemplate: 'templates/footerTemplate.html',
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
        
        
    // This function resizes the grid to fit. Currently fairly crude.
    function sizeGrid() {
        var height = $("body").height();
        
        height = height-$("#googleInfo").outerHeight();
        
        $("#view").height(height);
        
        height = height-$("#otherListStuff").outerHeight();
        
        
        //todo  why -20
        $("#grid").height(height-20);
        
        //height = height-55-30;
        //$("#grid .ngViewport").height(height);

    }
    // These calls 1.call the function sizeGrid upon loading, and attaches the event upon window resizing.
    sizeGrid();
    $(window).resize(sizeGrid);

    
    
    
    this.remove = function remove(index){
	    alert(index);
	$http.delete('/changerequests/' + $scope.crs[index].id,"").success(function() {
	    $scope.crs.splice(index,1);
	})};
    this.search = function search(){
	if ($scope.pagingOptions.currentPage != 1)
	    $scope.pagingOptions.currentPage = 1;
	else	    
	    $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage, $scope.searchParams);
    };
    this.getDrafts = function (){
	$http.get('/drafts').success(function(data){
	    $scope.crs = data.drafts;
	})};   
}]);

