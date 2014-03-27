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
            $scope.query = ""
            $scope.searchParams.forEach(function (s, index) {
                if (s.ignore) {
                    $scope.query += "NOT ";
                }
                if (s.field == "GLOBAL" && s.text) {
                    $scope.query += "(" + s.text + ") ";
                    
                    // match any
                    if (index != $scope.searchParams.length-1) {
                        if ($scope.match == 0) {
                            $scope.query += "OR ";
                        }
                    }
                }
                else if (s.field != "" && s.text) {
                    $scope.query += s.field + ":" + "(" + s.text + ")";
                    
                    if (index != $scope.searchParams.length-1) {
                        $scope.query += " ";
                        // match any
                        if ($scope.match == 0) {
                            $scope.query += "OR ";
                        }
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