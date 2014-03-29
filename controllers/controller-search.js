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

        $scope.sortableFields = [
            'technician',
            'peer_reviewer',
            'priority',
            'startTime',
            'endTime',
            'created_on',
            'author',
            'status'
        ];
        
        $scope.dateFields = [
            'created_on', 'startTime', 'endTime'
        ];
        
        $scope.searchParams = [{
            field: "GLOBAL",
            text: "",
            ignore: false,
            compare: ":",
        }, {
            field: "summary",
            text: "",
            ignore: false,
            compare: ":",
        }, {
            field: "technician",
            text: "",
            ignore: false,           
            compare: ":",
        }, {
            field: "priority",
            text: "routine",
            ignore: false,
            compare: ":",
        }, {
            field: "tags",
            text: "",
            ignore: false,
            compare: ":",
        }, {
            field: "startTime",
            text: "",
            ignore: false,
            compare: "<=",
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
                    $scope.query += s.field + s.compare + "(" + s.text + ")";
                    

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
        
        $scope.CreateTooltip = function(fieldName) {
            if (fieldName in $scope.dateFields) {
                return "dd-mm-yyyy";
            }
        }
        
    }
]);


app.directive('placehold', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attr, ctrl) {

            var value;

            var placehold = function () {
                if (scope.dateFields.indexOf(attr.placehold) >= 0) {
                    element.attr("placeholder", "yyyy-mm-dd");
                }
            };

            var unplacehold = function () {
                element.removeAttr('placeholder');
            };

            scope.$watch(attr.ngModel, function (val) {
                //alert(attr.ngModel);
                value = val || '';
            });

            scope.$watch(attr.placehold, function (val) {
                // this doesn't work.
                placehold();
            });
            
            element.bind('focus', function () {
                if (value === '') unplacehold();
            });

            element.bind('blur', function () {
                if (element.val() === '') placehold();
            });

            ctrl.$formatters.unshift(function (val) {
                if (!val) {
                    placehold();
                    value = '';
                    return "";
                }
                return val;
            });
        }
    };
});