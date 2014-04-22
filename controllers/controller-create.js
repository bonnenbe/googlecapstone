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
    $scope.saved = false;
    $scope.savedTime = null;
    var self = this;
    self.copy = {};
    angular.copy($scope.cr, self.copy);
    self.copy.tags = [];
    self.copy.cc_list = [];

    if ($location.path().indexOf('Template') == -1)
        self.cancelDrafts = $interval(function () {
            self.sendDraft($scope.cr);
        }, 5000);

    $scope.$on('$destroy', function () {
        $interval.cancel(self.cancelDrafts);
    });

    this.remove = function remove() {
        $http.delete('/api/drafts/' + $scope.cr.id).success(function () {});
    };

    this.add = function add(cr) {
        $interval.cancel(self.cancelDrafts);
        if (cr.id)
            self.remove();
        $http.post('/api/changerequests', JSON.stringify(cr)).success(function (data) {
            cr.id = data.id;
            console.log("Successful add");
            $location.path('/');
        }).error(function () {
            console.log("Unsuccessful add");
        });
    };
    this.addTemplate = function add(cr) {
        $http.post('/api/templates', JSON.stringify(cr)).success(function (data) {
            cr.id = data.id;
            console.log("Successful add");
            $location.path('/');
        }).error(function () {
            console.log("Unsuccessful add");
        });
    };

    this.sendDraft = function sendDraft(cr) {
        var changed = false;
        for (var prop in cr)
        {
            if (JSON.stringify(cr[prop]) !== JSON.stringify(self.copy[prop]))
            {
                changed = true;
                break;
            }
        }
        if (!changed)
            return; //no draft necessary        
        if (cr.id)
            $http.put('/api/drafts/' + cr.id, JSON.stringify(cr)).success(function (){
                 angular.copy(cr, self.copy);
                $scope.saved = true;
                $scope.savedTime = new Date();
            });
        else
            $http.post('/api/drafts', JSON.stringify(cr)).success(function (data) {
                cr.id = data.id;
                angular.copy(cr, self.copy);
                $scope.saved = true;
                $scope.savedTime = new Date();
            });
    };

    $scope.getTags = function (query) {
        var params = {};
        params["query"] = query;
        params["limit"] = 10;
        var obj = {};
        obj["params"] = params;
        return $http.get('/api/tags', obj);
    };

});
