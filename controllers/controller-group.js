app.controller('groupController', function ($routeParams, $http, $scope, $location) {

    $scope.group = {};

    this.add = function add(group) {
        $http.post('/usergroups', JSON.stringify(group)).success(function (data) {
            group.id = data.id;
            console.log("Successful add");
            $location.path('#');
        }).error(function () {
            console.log("Unsuccessful add");
        });
    };

});
