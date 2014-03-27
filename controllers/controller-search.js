app.controller('searchController', ['$http', '$scope', '$location', '$interval', '$routeParams',
    function ($http, $scope, $location, $interval, $routeParams) {

        // Note: initialization of sortfield is here and in search.html
        $scope.sortField = "created_on";
        $scope.direction = "descending";
        $scope.match = 1; // match all

        $scope.query = "";
        $scope.priorities = ['routine', 'sensitive'];
        $scope.status = ['draft', 'created', 'approved'];
        $scope.searchableFields = [
            'GLOBAL',
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

        $scope.searchParams = [{
            field: "GLOBAL",
            text: "",
            ignore: false
        }, {
            field: "summary",
            text: "",
            ignore: false
        }, {
            field: "technician",
            text: "",
            ignore: false            
        }, {
            field: "priority",
            text: "routine",
            ignore: false
        }, {
            field: "tags",
            text: "",
            ignore: false
        }, {
            field: "startTime",
            text: "",
            ignore: false
        }];


        this.buildQuery = function buildQuery() {
            $scope.query = "";
            var fields = 0;
            for (var i = 0; i < $scope.searchParams.length; i++) {
                if ($scope.searchParams[i].field != "" && $scope.searchParams[i].text) {
                    fields++;
                }
            }
            
            var count = 0;
            $scope.searchParams.forEach(function (s, index) {
                if (s.ignore) {
                    $scope.query += "NOT ";
                }
                if (s.field == "GLOBAL" && s.text) {
                    // increment count of valid fields
                    count++;
                    
                    $scope.query += "(" + s.text + ") ";
                    
                    // match any
                    if (count != fields && $scope.match == 0) {
                        $scope.query += "OR ";
                    }
                }
                else if (s.field != "" && s.text) {
                    
                    // increment count of valid fields
                    count++;
                    $scope.query += s.field + ":" + "(" + s.text + ")";
                    

                    $scope.query += " ";
                    // match any
                    if (count != fields && $scope.match == 0) {
                        $scope.query += "OR ";
                    }

                }

            });
        }

        this.search = function search() {

            this.buildQuery();
            $location.search('query', $scope.query);
            $location.search('sort', $scope.sortField);
            $location.search('direction', $scope.direction);
            $location.path("/");
        }
    }
]);