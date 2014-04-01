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
            {field:'GLOBAL', display: 'GLOBAL'},
            {field:'id', display: 'ID'},
            {field:'summary', display:'Summary'},
            {field:'description', display: 'Description'},
            {field:'impact', display: 'Impact'},
            {field:'documentation', display: 'Documentation'},
            {field:'rationale', display:'Rationale'},
            {field:'implementation_steps', display: 'Implementation Steps'},
            {field:'technician', display: 'Technician'},
            {field:'peer_reviewer', display: 'Peer Reviewer'},
            {field:'priority', display: 'Priority'},
            {field:'tests_conducted', display: 'Tests Conducted'},
            {field:'risks', display: 'Risks'},
            {field:'backout_plan', display: 'Backout Plan'},
            {field:'communication_plan', display: 'Communication Plan'},
            {field:'layman_description', display: 'Layman Description'},
            {field:'startTime', display: 'Start Time'},
            {field:'endTime', display: 'End Time'},
            {field:'tags', display: 'Tags'},
            {field:'cc_list', display: 'CC List'},
            {field:'created_on', display: 'Created On'},
            {field:'author', display: 'Author'},
            {field:'status', display: 'Status'}
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
            compare: "=",
        }, {
            field: "summary",
            text: "",
            compare: "=",
        }, {
            field: "technician",
            text: "",
            compare: "=",
        }, {
            field: "priority",
            text: "",
            compare: "=",
        }, {
            field: "tags",
            text: "",
            compare: "=",
        }, {
            field: "startTime",
            text: "",
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
            
                if (!s.field || !s.text) {
                    return;
                }
            
                // if != then add NOT before all else, change compare to =
                if (s.compare == "!=") {
                    $scope.query += "NOT ";
                    s.compare = "=";
                }

                // cut out whitespace
                s.text = s.text.trim();
                
                if (s.text.indexOf(" ") >= 0) {
                    s.text = "("+s.text+")";
                }

                if (s.field == "GLOBAL") {
                    // increment count of valid fields
                    count++;
                    
                    $scope.query += s.text + " ";
                    
                    // match any
                    if (count != fields && $scope.match == 0) {
                        $scope.query += "OR ";
                    }
                }
                else {
                    
                    // increment count of valid fields
                    count++;
                    $scope.query += s.field + s.compare + s.text;
                    
                    $scope.query += " ";
                    
                    // match any
                    if (count != fields && $scope.match == 0) {
                        $scope.query += "OR ";
                    }
                }
            });
            // remove ending whitespace
            $scope.query = $scope.query.trim();
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