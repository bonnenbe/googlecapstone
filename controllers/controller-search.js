app.controller('searchController', ['$http', '$scope', '$location', '$interval',
    function ($http, $scope, $location, $interval) {

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

        $scope.searchParams = [{
            field: $scope.searchableFields[0],
            text: ""
        }];
        
        
        this.search = function search() {
            alert("hi")
        }
        
        
    }
]);
