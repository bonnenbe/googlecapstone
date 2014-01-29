angular.module('module1',[])
    .controller('controller1',['$http', function($http){
	this.priorities = ['routine', 'sensitive'];
	this.crs = [];
			
	this.add = function add(cr){
	    newcr = new Object();
	    for(var k in cr) newcr[k]=cr[k];
	    this.crs.push(newcr);
	    $http.post('/changerequests',JSON.stringify(newcr)).success(function() {
	    	window.alert("SUCCESS");
	    }).error(function() {
	    	window.alert("ERROR");
	    });
	};
	this.remove = function remove(index){
	    this.crs.splice(index,1);
	};
    }]);
