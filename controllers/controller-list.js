// List(main page) Controller
app.controller('listController', function ($http, $scope, $location, Users, $interval) {
    $scope.search = {};
    angular.extend($scope.search, $location.search());
    var self = this;
    $scope.priorities = ['routine', 'sensitive'];
    $scope.status = ['draft', 'created', 'approved', 'succeeded', 'failed'];
    $scope.pagingOptions = {
        pageSizes: [10, 20, 50, 100],
        pageSize: 20,
        currentPage: 1,
        totalServerItems: false
    };
    Users.getUser().then(function(response){
        $scope.pagingOptions.pageSize = response.data.preferences.resultsPerPage;
    });

        // Sets paging data
        $scope.setPagingData = function (pageSize, page, data) {
            $scope.crs = data;
            if (!$scope.$$phase) {
                $scope.$apply();
            }
            sizeGrid();
        };

        // On get new page
        $scope.getPagedDataAsync = function (pagingOptions, search) {
            var params = {};
            var pageSize = pagingOptions.pageSize;
            var page = pagingOptions.currentPage;
            params["offset"] = (page - 1) * pageSize;
            params["limit"] = pageSize;
            
            angular.extend(params, search);
            var obj = {};
            

            var query = search.query;
            var mode = search.mode;
            if (params.mode)
                delete params.mode;
            obj["params"] = params;
            
            if (mode == "approval") {
                if (query)
                    obj["params"]["query"] = encodeURIComponent("status:created priority:sensitive (" + query + ")");
                else
                    obj["params"]["query"] = encodeURIComponent("status:created priority:sensitive");
                $http.get('/api/changerequests', obj).success(function (data) {
                    $scope.setPagingData(pageSize, page, data);
                });
            }
            else if (mode == 'recentlyApproved') {
                var weekago = new Date();
                weekago.setDate(weekago.getDate() - 7);
                var date = weekago.toJSON().substring(0, 10);
                if (query)
                    obj["params"]["query"] = encodeURIComponent("status:approved priority:sensitive approved_on >= " + date + " (" + query + ")");
                else
                    obj["params"]["query"] = encodeURIComponent("status:approved priority:sensitive approved_on >= " + date);

                $http.get('/api/changerequests', obj).success(function (data) {
                    $scope.setPagingData(pageSize, page, data);
                });
            }
            else if (mode == "drafts")
                $http.get('/api/drafts', obj).success(function (data) {
                    $scope.setPagingData(pageSize, page, data);
                });
            else if (mode == 'templates')
                $http.get('/api/templates', obj).success(function (data) {
                    $scope.setPagingData(pageSize, page, data);
                });
            else //default = all change requests
                $http.get('/api/changerequests', obj).success(function (data) {
                    $scope.setPagingData(pageSize, page, data);
                });
        };


        // restart: if true, restart from first page
        $scope.refresh = function (restart) {
            restart = typeof restart !== "undefined" ? restart : false;
            if (restart)
                if ($scope.pagingOptions.currentPage != 1)
                    $scope.pagingOptions.currentPage = 1;
                else 
                    $scope.getPagedDataAsync($scope.pagingOptions, $scope.search);
            else 
                $scope.getPagedDataAsync($scope.pagingOptions, $scope.search);
        };

        //
        // Events for setting paging data when paging data is changed or page is turned	
        //


        $scope.refresh();

        $scope.$watch('pagingOptions', function (newVal, oldVal) {
            if (newVal !== oldVal)
                $scope.refresh();
        }, true);

        $scope.$watch('search.mode', function (newVal, oldVal) {
            if (newVal !== oldVal)
                $scope.refresh(true);
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
            rowTemplate: 'static/templates/gridRow.html',
            footerTemplate: 'static/templates/footerTemplate.html',
            totalServerItems: 'totalServerItems',
            pagingOptions: $scope.pagingOptions,
            filterOptions: $scope.filterOptions,
            enableColumnResize: true,
            useExternalSorting: true,
            columnDefs: [{
                    field: "created_on | datetime",
                displayName: "Created On",
                width: 160
                }, {
                    field: "startTime | datetime",
                    displayName: "Start Time",
                    width: 160,
                    cellTemplate: 'static/templates/cell.html'
                }, {
                    field: "technician",
                    displayName: "Technician",
                    width: 200,
                    cellTemplate: 'static/templates/cell.html'
                }, {
                    field: "priority",
                    displayName: "Priority",
                    width: 80,
                    cellTemplate: 'static/templates/cell.html'
                }, {
                    field: "status",
                    displayName: "Status",
                    width: 80,                  
                    cellTemplate: 'static/templates/cell.html'
                }, {
                    field: "summary",
                    displayName: "Summary",                  
                    cellTemplate: 'static/templates/cell.html'
                }
                //			{ field:"", displayName: "delete", cellTemplate:'<div class="ngCellText"><a ng-href ng-click="ctrl.remove(1)">[X]</a></div>'}
            ]
        };
        
        $scope.$watch('gridOptions.ngGrid.config.sortInfo', function (newVal, oldVal) {
            if (newVal !== oldVal)
            {
                if (newVal && newVal.fields && newVal.fields.length)
                    $scope.search.sort = newVal.fields[0].split(' ')[0];
                if (newVal && newVal.directions && newVal.directions.length)
                    $scope.search.direction = newVal.directions[0];
                self.search();
                
            }
        }, true);

        this.redirect = function (index) {
            $location.path('/id=' + ($scope.crs[index].id)).toString();
        }

        //
        // Resizing grid
        //

        // This function resizes the grid to fit. Currently fairly crude.
        function sizeGrid() {
            var height = $("body").height();

            //todo  why -10
            height = height - $("#navbar").outerHeight(true) + 20;
            //$("#view").height(height);

            height = height - $("#otherListStuff").outerHeight(true);
            $("#grid").height(height);
            
            // This fails...
            //$("#grid").height(20*$scope.pagingOptions.pageSize+55+30);

        }
        // These calls 1.call the function sizeGrid upon loading, and attaches the event upon window resizing.
        sizeGrid();
        $(window).resize(sizeGrid);

        this.search = function search() {
            var search = angular.copy($scope.search);
            if (search.mode)
                delete search.mode;
            $location.search(search);
            $scope.refresh();
            $('#fullSearch input').focus();
        };

        this.clearDrafts = function () {
            $http.delete('/api/drafts').success(function () {
                $scope.refresh();
            })
        };
        var init = function (){
            $('#fullSearch input').focus();
            sizeGrid();

        };
        init();
});
