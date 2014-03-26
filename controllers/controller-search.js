app.controller('searchController', ['$http', '$scope', '$location', '$interval', '$routeParams',
    function ($http, $scope, $location, $interval, $routeParams) {

        // Note: initialization of sortfield is here and in search.html
        $scope.sortField = "created_on";
        $scope.direction = "descending";
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
            text: ""
        }, {
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
        }];


        this.buildQuery = function buildQuery() {
            $scope.query = ""
            $scope.searchParams.forEach(function (s) {
                if (s.field == "GLOBAL" && s.text) {
                    $scope.query += s.text + " ";
                }
                else if (s.field != "" && s.text) {
                    $scope.query += s.field + ":" + s.text;
                    $scope.query += " ";
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