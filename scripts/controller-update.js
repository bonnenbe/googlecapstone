
app.controller('updateController', function($routeParams, $http, $scope, $location){
	$scope.priorities = ['routine', 'sensitive'];
	$http.get('/changerequests/' + $routeParams.id,"").success(function(data) {
	    $scope.cr = data.changerequest;
	    $scope.cr.startDate = new Date($scope.cr.startTime);
	    $scope.cr.startTime = new Date($scope.cr.startTime);
	    $scope.cr.endDate = new Date($scope.cr.endTime);
	    $scope.cr.endTime = new Date($scope.cr.endTime);
	});

	this.update = function update(cr){
	    $http.put('/changerequests/' + $routeParams.id,JSON.stringify(cr)).success(function(data) {
		$location.path('#');
	    })};
		
});
