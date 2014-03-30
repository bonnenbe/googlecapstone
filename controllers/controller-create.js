app.controller('createController', function ($http, $scope, $location, $interval) {
    $scope.priorities = ['routine', 'sensitive'];
    $scope.cr = {};
    $scope.cr.technician = $scope.user;
    $scope.cr.priority = 'routine';
    $scope.cr.startTime = new Date();
    $scope.cr.endTime = new Date();
    $scope.cr.startTime.setMinutes(0);
    $scope.cr.startTime.setSeconds(0);
    $scope.cr.endTime.setMinutes(0);
    $scope.cr.endTime.setSeconds(0);
    $scope.cr.id = null;
    var self = this;

    this.onload = function onload() {
        $scope.heading = "Create Change Request";
        $("#heading").text($scope.heading);
    }
    if ($location.path().indexOf('Template') == -1)
        self.cancelDrafts = $interval(function () {
            self.sendDraft($scope.cr);
        }, 5000);

    $scope.$on('$destroy', function () {
        $interval.cancel(self.cancelDrafts);
    });

    this.remove = function remove() {
        $http.delete('/drafts/' + $scope.cr.id).success(function () {});
    };

    this.add = function add(cr) {
        $interval.cancel(self.cancelDrafts);
        if (cr.id)
            self.remove();
        $http.post('/changerequests', JSON.stringify(cr)).success(function (data) {
            cr.id = data.id;
            console.log("Successful add");
            $location.path('#');
        }).error(function () {
            console.log("Unsuccessful add");
        });
    };
    this.addTemplate = function add(cr) {
        $http.post('/templates', JSON.stringify(cr)).success(function (data) {
            cr.id = data.id;
            console.log("Successful add");
            $location.path('#');
        }).error(function () {
            console.log("Unsuccessful add");
        });
    };

    this.sendDraft = function sendDraft(cr) {
        if (cr.id)
            $http.put('/drafts/' + cr.id, JSON.stringify(cr));
        else
            $http.post('/drafts', JSON.stringify(cr)).success(function (data) {
                cr.id = data.id;
            });
    };

    $scope.getTags = function (query) {
        var params = {};
        params["query"] = query;
        params["limit"] = 10;
        var obj = {};
        obj["params"] = params;
        return $http.get('/tags', obj);
    };

});
