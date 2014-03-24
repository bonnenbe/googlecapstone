// List(main page) Controller
app.controller('listController', ['$http', '$scope', '$location',
    function ($http, $scope, $location) {
        var self = this;
        $scope.mode = "all"
        $scope.priorities = ['routine', 'sensitive'];
        $scope.status = ['draft', 'created', 'approved', 'succeeded', 'failed'];
        $scope.searchableFields = ['technician', 'priority'];
        $scope.searchParams = [{
            field: $scope.searchableFields[0],
            text: ""
        }];

        $scope.filterOptions = {
            filterText: "",
            useExternalFilter: true
        };

        $scope.totalServerItems = 0;
        $scope.pagingOptions = {
            pageSizes: [10, 20, 50, 100],
            pageSize: 10,
            currentPage: 1,
            totalServerItems: false
        };

        // Sets paging data
        $scope.setPagingData = function (pageSize, page, data) {
            $scope.crs = data;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
        };

        // On get new page
        $scope.getPagedDataAsync = function (pageSize, page, searchParams, mode, query) {
            setTimeout(function () {
                var params = {};
                params["offset"] = (page - 1) * pageSize;

                // Send full text query
                if (!query)
                    query = ""
                params["query"] = encodeURIComponent(query);


                params["limit"] = pageSize;
                searchParams.forEach(function (s) {
                    if (s.text) params[s.field] = s.text;
                });
                var obj = {};

                obj["params"] = params;
                if (mode == "approval") {
                    if (query)
                        obj["params"]["query"] = encodeURIComponent("status:created priority:sensitive (" + query + ")");
                    else
                        obj["params"]["query"] = encodeURIComponent("status:created priority:sensitive");
                    $http.get('/changerequests', obj).success(function (data) {
                        $scope.setPagingData(pageSize, page, data.changerequests);
                    });
                }
		else if (mode == 'recentlyApproved')
		{
		    var weekago = new Date();
		    weekago.setDate(weekago.getDate() - 7);
		    var date = weekago.toJSON().substring(0,10);
		    if (query)
			obj["params"]["query"] = encodeURIComponent("status:approved priority:sensitive approved_on >= " + date + " (" + query + ")");
		    else
			obj["params"]["query"] = encodeURIComponent("status:approved priority:sensitive approved_on >= " + date);

		    $http.get('/changerequests', obj).success(function (data){
			$scope.setPagingData(pageSize, page, data.changerequests);
                    });
		}
		else if (mode == "drafts")
                    $http.get('/drafts', obj).success(function (data) {
                        $scope.setPagingData(pageSize, page, data.drafts);
                    });
                else if (mode == 'templates')
                    $http.get('/templates', obj).success(function (data) {
                        $scope.setPagingData(pageSize, page, data.templates);
                    });
                else
                    $http.get('/changerequests', obj).success(function (data) {
                        $scope.setPagingData(pageSize, page, data.changerequests);
                    });

            }, 100);
        };

        $scope.refresh = function () {
            $scope.getPagedDataAsync($scope.pagingOptions.pageSize, $scope.pagingOptions.currentPage,
                $scope.searchParams, $scope.mode, $scope.query);
        };




        //
        // Events for setting paging data when paging data is changed or page is turned	
        //
        $scope.refresh();

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal)
                $scope.refresh();
        }, true);

        $scope.$watch('filterOptions', function (newVal, oldVal) {
            if (newVal !== oldVal)
                $scope.refresh();
        }, true);

        //
        // Grid Options
        //

        // for the column definitions
        var cellTemplate = '<div class="ngCellText" ng-class="col.colIndex()"><a ng-href="#/id={{row.getProperty(col.field)}}">{{row.getProperty(col.field)}}</a></div>'

        $scope.gridOptions = {
            data: 'crs',
            enablePaging: true,
            showFooter: true,
            rowTemplate: 'templates/gridRow.html',
            footerTemplate: 'templates/footerTemplate.html',
            totalServerItems: 'totalServerItems',
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions,
            enableColumnResize: true,
            columnDefs: [{
                    field: "created_on | datetime",
                    displayName: "Created On"
                }, {
                    field: "technician",
                    displayName: "Technician"
                }, {
                    field: "summary",
                    displayName: "Summary"
                }, {
                    field: "priority",
                    displayName: "Priority"
                }, {
                    field: "startTime | datetime",
                    displayName: "Start Time"
                }, {
                    field: "endTime | datetime",
                    displayName: "End Time"
                }, {
                    field: "status",
                    displayName: "Status"
                }, {
                    field: "id",
                    displayName: "ID"
                }
                //			{ field:"", displayName: "delete", cellTemplate:'<div class="ngCellText"><a ng-href ng-click="ctrl.remove(1)">[X]</a></div>'}
            ]
        };

        this.redirect = function (index) {
            $location.path('/id=' + ($scope.crs[index].id)).toString();
        }


        //
        // Resizing grid
        //

        // This function resizes the grid to fit. Currently fairly crude.
        function sizeGrid() {
            var height = $("body").height();

            //todo  why -20
            height = height - $("#googleInfo").outerHeight() - 20;
            $("#view").height(height);
            //
            height = height - $("#otherListStuff").outerHeight();
            $("#grid").height(height);

        }
        // These calls 1.call the function sizeGrid upon loading, and attaches the event upon window resizing.
        sizeGrid();
        $(window).resize(sizeGrid);


        // Currently not called anywhere. Remove the change request at an *index* in the grid
        this.remove = function remove(index) {
            alert(index);
            $http.delete('/changerequests/' + $scope.crs[index].id, "").success(function () {
                $scope.crs.splice(index, 1);
            });
        };

        /////// todo fix test full search function
        this.fullsearch = function fullsearch() {
            $scope.refresh();
        }

        this.search = function search() {
            if ($scope.pagingOptions.currentPage != 1)
                $scope.pagingOptions.currentPage = 1;
            else
                $scope.refresh();
        };

        this.clearDrafts = function () {
            $http.delete('/drafts').success(function () {
                $scope.refresh();
            })
        };
        $scope.onSelectCRs = function () {
            $scope.mode = "all";
            $scope.refresh();
        };
        $scope.onSelectMyDrafts = function () {
            $scope.mode = "drafts";
            $scope.refresh();
        };
        $scope.onSelectApproval = function () {
            $scope.mode = "approval";
            $scope.refresh();
        };
	$scope.onSelectRecentlyApproved = function() {
	    $scope.mode = "recentlyApproved";
	    $scope.refresh();
	};
	$scope.onSelectTemplates = function() {
	    $scope.mode = "templates";
	    $scope.refresh();
	};

    }
]);
