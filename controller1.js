angular.module('module1',[])
    .controller('controller1',function(){
	this.priorities = ['routine', 'sensitive'];
	this.crs = [];
			
	this.add = function add(cr){
	    newcr = new Object();
	    for(var k in cr) newcr[k]=cr[k];
	    this.crs.push(newcr);
	};
    });
