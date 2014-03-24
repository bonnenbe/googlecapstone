app.controller('searchController', ['$http', '$scope', '$location', '$interval', '$routeParams',
    function ($http, $scope, $location, $interval, $routeParams) {

        $scope.query = "";
        $scope.priorities = ['routine', 'sensitive'];
        $scope.status = ['draft', 'created', 'approved'];
        $scope.searchableFields = [
            'summary',
            'description',
            'impact',
            'documentation',
            'rationale',
            'implementation_steps',
            'technician',
            'peer_reviewer',
            'priority',
            'tests_conducted',
            'risks',
            'backout_plan',
            'communication_plan',
            'layman_description',
            'startTime',
            'endTime',
            'tags',
            'cc_list',
            'created_on',
            'author',
            'status'
        ];

        $scope.searchParams = [
            {
                field: "summary",
                text: ""
            }, {
                field: "technician",
                text: ""
            }, {
                field: "priority",
                text: "routine"
            }, {
                field: "tags",
                text: ""
            }, {
                field: "startTime",
                text: ""
            }
        ];
        
        
        this.buildQuery = function buildQuery() {
            $scope.query = ""
            $scope.searchParams.forEach(function (s) {
                if (s.field != "" && s.text) { 
                    $scope.query += s.field + ":" + s.text;
                    $scope.query += " ";
                }
                
            });

        }
        
        this.search = function search() {
        
            
            this.buildQuery();            
            alert($scope.query);
            
            $location.url("/?query="+$scope.query);
            //$location.search({query:$scope.query});
            //$location.path("#");
            
            // var params = {};
            // params["offset"] = 0;

            // // Send full text query
            // if (!query)
                // query = "asdf";
            // params["query"] = encodeURIComponent(query);

            // params["limit"] = 10;
            // //searchParams.forEach(function (s) {
            // //    if (s.text) params[s.field] = s.text;
            // //});
            // var obj = {};

            // obj["params"] = params;
        
            // obj["params"]["query"] = encodeURIComponent(query);
            // $http.get('/changerequests', obj).success(function (data) {
                // alert("not linked yet");
            // });
            
        }
        
        
    }
]);
