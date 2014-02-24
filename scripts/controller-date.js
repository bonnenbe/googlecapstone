app.controller('DateCtrl', function($scope){
    $scope.format = 'dd-MMMM-yyyy';
    $scope.dateOptions = {};
    $scope.open = function($event) {
	$event.preventDefault();
	$event.stopPropagation();
	$scope.opened = true;
    };
});

