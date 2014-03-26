app.controller('preferencesController', function ($scope, $location, $http) {
    
    $scope.submit = function() {
        $http.put('/user', $scope.preferences).success(function(){
            $location.path('/');
        });
    };
    $scope.reset = function() {
        $http.delete('/user').success(function(){
            $http.get('/user').success(function(data){
                Object.keys(data.preferences).forEach(function (k){
                    $scope.preferences[k] = data.preferences[k];
                });
                $location.path('/');
            });
        });
    };
});