app.controller('DateCtrl', function ($scope) {
    $scope.popup = {};
    $scope.format = 'dd-MMMM-yyyy';
    $scope.dateOptions = {};
    $scope.open = function ($event) {
        $event.preventDefault();
        $event.stopPropagation();
        $scope.popup.opened = true;
    };
});
