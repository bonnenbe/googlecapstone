app.controller('updateController', function ($routeParams, $http, $scope, $location) {
    $scope.priorities = ['routine', 'sensitive'];
    $scope.status = ['created', 'approved', 'draft'];


    this.onload = function onload() {
        $scope.heading = "Edit Change Request";
        $("#heading").text($scope.heading);

    }

    $http.get('/changerequests/' + $routeParams.id, "").success(function (data) {
        $scope.cr = data.changerequest;
        $scope.cr.startTime = new Date($scope.cr.startTime);
        $scope.cr.endTime = new Date($scope.cr.endTime);
        $scope.showComment = ($scope.cr.status == 'created' || $scope.cr.status == 'approved');
    });

    this.update = function update(cr) {
        if (cr.status == 'draft' && $routeParams.id.indexOf("-") == -1)
        //singleton draft
        {
            $http.post('/changerequests', JSON.stringify(cr)).success(function (data) {
                cr.id = data.id;
                $http.delete('/drafts/' + $routeParams.id);
                $location.path('#');
            });
        } else if (cr.status == 'draft' && $routeParams.id.indexOf("-") != -1)
        //child draft
        {
            var hyphen = $routeParams.id.lastIndexOf("-");
            var parentID = $routeParams.id.slice(0, hyphen);
            var draftID = $routeParams.id;
            $http.put('/changerequests/' + parentID, JSON.stringify(cr)).success(function (data) {
                cr.id = parentID;
                $http.delete('/drafts/' + draftID).success(function (data) {
                    $location.path('#');
                });
            });
        } else if (cr.status == 'template')
        {
            $http.put('/templates/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
                $location.path('#');
            });
        }
        else //created or approved
            $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
                $location.path('#');
            });
    };

    this.approve = function approve(cr) {
        cr.status = 'approved';
        $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('#');
        })
    };
    this.succeeded = function approve(cr, a) {
        if(a == true) {
            cr.status = 'succeeded';
            $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('#');
            })
        } else {
            cr.status = 'failed';
            $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr)).success(function (data) {
            $location.path('#');
            })
        }
    };
    this.subscribe = function subscribe(cr){
        $scope.cr.cc_list.push($scope.user);
        $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr));
    };
    this.unsubscribe = function unsubscribe(cr){
        $scope.cr.cc_list.splice($scope.cr.cc_list.indexOf($scope.user),1)
        $http.put('/changerequests/' + $routeParams.id, JSON.stringify(cr));
    };
    this.sendDraft = function sendDraft(cr) {
        if (cr.status == 'draft')
            $http.put('/drafts/' + cr.id, JSON.stringify(cr));
        else
            $http.post('/drafts', JSON.stringify(cr)).success(function (data) {
                $http.get('/drafts/' + data.id).success(function (data) {
                    cr = data.draft;
                });
            });
    };
    this.clone = function(cr){
            $http.post('/templates', JSON.stringify(cr)).success(function (data) {
                $location.path('/id=' + data.id);
            });
    };
    this.templateToDraft = function(cr){
        $http.post('/drafts', JSON.stringify(cr)).success(function (data) {
            $location.path('/id=' + data.id);
        });
    };
    $scope.unapprove = function (){
        $scope.cr.status = 'created';
        $http.put('changerequests/' + $scope.cr.id, $scope.cr)
    }
        
    
    $scope.getTags = function (query) {
        var params = {};
        params["query"] = query;
        params["limit"] = 10;
        var obj = {};
        obj["params"] = params;
        return $http.get('/tags', obj);
    };
});

