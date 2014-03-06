app.controller('updateController', function($routeParams, $http, $scope, $location){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.status = ['created', 'approved', 'draft'];

    
    this.onload = function onload() {
        $scope.heading = "Edit Change Request";
        $("#heading").text($scope.heading);

    }
 
	$http.get('/changerequests/' + $routeParams.id,"").success(function(data) {
	    $scope.cr = data.changerequest;
	    $scope.cr.startTime = new Date($scope.cr.startTime);
	    $scope.cr.startTime.setTime($scope.cr.startTime.getTime() - $scope.cr.startTime.getTimezoneOffset() * 60000);
	    $scope.cr.endTime = new Date($scope.cr.endTime);
	    $scope.cr.endTime.setTime($scope.cr.endTime.getTime() - $scope.cr.endTime.getTimezoneOffset() * 60000);
	});

    this.update = function update(cr){
	if (cr.status == 'draft' && $routeParams.id.indexOf("-") == -1)
	    //singleton draft
	{
	    $http.post('/changerequests',JSON.stringify(cr)).success(function(data){
		cr.id = data.id;
		$http.delete('/drafts/' + $routeParams.id);
		$location.path('#');
	    });
	}
	else if (cr.status == 'draft' && $routeParams.id.indexOf("-") != -1)
	    //child draft
	{
	    var hyphen = $routeParams.id.lastIndexOf("-");
	    var parentID = $routeParams.id.slice(0,hyphen);
	    var draftID = $routeParams.id;
	    $http.put('/changerequests/' + parentID,JSON.stringify(cr)).success(function(data) {
		cr.id = parentID;
		$http.delete('/drafts/' + draftID).success(function(data) {
		    $location.path('#');
		});
	    });
	}
	else //created or approved
	    $http.put('/changerequests/' + $routeParams.id,JSON.stringify(cr)).success(function(data) {
		$location.path('#');
	    });
    };

    this.approve = function approve(cr){
	$http.put('/approve/' + $routeParams.id,JSON.stringify(cr)).success(function(data) {
	    $location.path('#');
	})
    };
    this.sendDraft = function sendDraft(cr){
        if (cr.status == 'draft')
            $http.put('/drafts/' + cr.id, JSON.stringify(cr));
        else
            $http.post('/drafts', JSON.stringify(cr)).success(function(data){
               	$http.get('/drafts/' + data.id).success(function(data){
		    cr = data.draft;
		});
            });
    };
    
});


// This function is used to close the audit trail button. It's a part of a bootstrap demo.
function CollapseDemoCtrl($scope) {
    $scope.isCollapsed = false;
}
