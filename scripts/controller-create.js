
app.controller('createController', function($http,$scope,$location,$interval){
    $scope.priorities = ['routine', 'sensitive'];
    $scope.cr = {};
    $scope.cr.technician = $scope.user;
    $scope.cr.startTime = new Date();
    $scope.cr.endTime = new Date();
    $scope.cr.startTime.setMinutes(0);
    $scope.cr.endTime.setMinutes(0);
    $scope.cr.id = ""
    var self = this;
    self.cancelDrafts = $interval(function (){
	self.sendDraft($scope.cr);
    }, 10000);
    $scope.$on('$destroy', function() {
	$interval.cancel(self.cancelDrafts);
    });
    this.remove = function remove(){
	$http.delete('/changerequests/' + $scope.cr.id).success(function(){
	})};
    this.add = function add(cr){
	$interval.cancel(self.cancelDrafts);
	if (cr.id)
	    self.remove();
	$http.post('/changerequests',JSON.stringify(cr)).success(function(data) {
	    cr.id = data.id;
	    console.log("Successful add");
	    $location.path('#');
	}).error(function() {
	    console.log("Unsuccessful add");
	});
    };    
    this.sendDraft = function sendDraft(cr){
	$http.post('/drafts', JSON.stringify(cr)).success(function(data){
	    cr.id = data.id;
	})}; 
    
});

