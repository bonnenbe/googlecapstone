app.controller('updateController', function ($routeParams, $http, $scope, $location, $interval) {
    $scope.priorities = ['routine', 'sensitive'];
    $scope.status = ['created', 'approved', 'draft'];
    var self = this;
    self.draftID = null;
    self.copy = {};
    $scope.saved = false;
    $scope.savedTime = null;
    $http.get('/api/changerequests/' + $routeParams.id, "").success(function (data) {
        $scope.cr = data;
        $scope.cr.startTime = new Date($scope.cr.startTime);
        $scope.cr.endTime = new Date($scope.cr.endTime);
        $scope.showComment = $.inArray($scope.cr.status, ['draft', 'template']) < 0;
        angular.copy($scope.cr, self.copy);
        if (data.status != 'template')
            self.cancelDrafts = $interval(function () {
                self.sendDraft();
            }, 5000);     
        if (data.status == 'draft')
            self.draftID = data.id;
    });

    $scope.$on('$destroy', function () {
        $interval.cancel(self.cancelDrafts);
    });

    this.update = function update(cr) {
        if (cr.status == 'draft' && $routeParams.id.indexOf("-") == -1)
        //singleton draft
        {
            $http.post('/api/changerequests', JSON.stringify(cr)).success(function (data) {
                cr.id = data.id;
                $http.delete('/api/drafts/' + $routeParams.id);
                $location.path('/');
            });
        } else if (cr.status == 'draft' && $routeParams.id.indexOf("-") != -1)
        //child draft
        {
            var hyphen = $routeParams.id.lastIndexOf("-");
            var parentID = $routeParams.id.slice(0, hyphen);
            var draftID = $routeParams.id;
            $http.put('/api/changerequests/' + parentID, JSON.stringify(cr)).success(function (data) {
                cr.id = parentID;
                $http.delete('/api/drafts/' + draftID).success(function (data) {
                    $location.path('/');
                });
            });
        } else if (cr.status == 'template')
        {
            $http.put('/api/templates/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
                $location.path('/');
            });
        }
        else //created or approved
            $http.put('/api/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
                $http.delete('/api/drafts/' + self.draftID).success(function (data) {
                    $location.path('/');
                });
            });
    };

    this.approve = function approve(cr) {
        cr.status = 'approved';
        $http.put('/api/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('/');
        })
    };
    this.succeeded = function approve(cr, a) {
        if(a == true) {
            cr.status = 'succeeded';
            $http.put('/api/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('/');
            })
        } else {
            cr.status = 'failed';
            $http.put('/api/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('/');
            })
        }
    };
    this.subscribe = function subscribe(){
        $scope.cr.cc_list.push($scope.user);
        $http.put('/api/api/changerequests/' + $routeParams.id, $scope.cr);
    };
    this.unsubscribe = function unsubscribe(){
        $scope.cr.cc_list.splice($scope.cr.cc_list.indexOf($scope.user),1)
        $http.put('/api/api/changerequests/' + $routeParams.id, $scope.cr);
    };
    this.sendDraft = function sendDraft() {
        var changed = false;
        for (var prop in $scope.cr)
        {
            if (JSON.stringify($scope.cr[prop]) !== JSON.stringify(self.copy[prop]))
            {
                changed = true;
                break;
            }
        }
        if (!changed)
            return; //no draft necessary
        if (self.draftID)
            $http.put('/api/drafts/' + self.draftID, JSON.stringify($scope.cr)).success(function (){
                 angular.copy($scope.cr, self.copy);
                $scope.saved = true;
                $scope.savedTime = new Date();
            });
        else
            $http.post('/api/drafts', $scope.cr).success(function (data) {
                self.draftID = data.id;
                angular.copy($scope.cr, self.copy);
                $scope.saved = true;
                $scope.savedTime = new Date();
            });
    };
    this.getRemovals = function(from_list, to_list){
        var remove_list = [];
        for(var i=0; i<from_list.length; i++)
        {
            if (to_list.indexOf(from_list[i]) < 0)
            {
                remove_list.push(from_list[i]);
            }
        }
        return remove_list;
    };
    this.getAdditions = function(from_list, to_list){
        var add_list = [];
        for(var i=0; i<to_list.length; i++)
        {
            if (from_list.indexOf(to_list[i]) < 0)
            {
                add_list.push(to_list[i]);
            }
        }
        return add_list;
    };
    this.clone = function(){
        $http.post('/api/templates', $scope.cr).success(function (data) {
                $location.path('/id=' + data.id);
            });
    };
    this.templateToDraft = function(){
        $http.post('/api/drafts', $scope.cr).success(function (data) {
            $location.path('/id=' + data.id);
        });
    };
    $scope.unapprove = function (){
        $scope.cr.status = 'created';
        $http.put('/api/changerequests/' + $scope.cr.id, $scope.cr)
    }
        
    
    $scope.getTags = function (query) {
        var params = {};
        params["query"] = query;
        params["limit"] = 10;
        var obj = {};
        obj["params"] = params;
        return $http.get('/api/tags', obj);
    };
});

