var app = angular.module('module1', ['ngRoute', 'ngGrid', 'ui.bootstrap', 'ngTagsInput']);

//
// Main Controller
//
app.controller('main', function ($http, $scope, $window, $location) {
    $http.get('/user').success(function (data) {
        $scope.user = data.user;
        $scope.inAdmins = data.inAdmins;
        $scope.inCommittee = data.inCommittee;
        $scope.preferences = data.preferences;
    });
    $scope.onEnter = function (event, foo) {
        if (event.which == 13)
            foo.call();
    };
    $scope.link = function (path){
        $window.location.pathname = path;
    };
    $scope.isPath = function (path){
        return $location.path() == path;
    };
});

// For autosizing text areas
// https://gist.github.com/thomseddon/4703968

app.directive('autoGrow', function() {
	return function(scope, element, attr){
		var minHeight = element[0].offsetHeight,
			paddingLeft = element.css('paddingLeft'),
			paddingRight = element.css('paddingRight');
 
		var $shadow = angular.element('<div></div>').css({
			position: 'absolute',
			top: -10000,
			left: -10000,
			width: element[0].offsetWidth - parseInt(paddingLeft || 0) - parseInt(paddingRight || 0),
			fontSize: element.css('fontSize'),
			fontFamily: element.css('fontFamily'),
			lineHeight: element.css('lineHeight'),
			resize:     'none'
		});
		angular.element(document.body).append($shadow);
 
		var update = function() {
			var times = function(string, number) {
				for (var i = 0, r = ''; i < number; i++) {
					r += string;
				}
				return r;
			}
 
			var val = element.val().replace(/</g, '&lt;')
				.replace(/>/g, '&gt;')
				.replace(/&/g, '&amp;')
				.replace(/\n$/, '<br/>&nbsp;')
				.replace(/\n/g, '<br/>')
				.replace(/\s{2,}/g, function(space) { return times('&nbsp;', space.length - 1) + ' ' });
			$shadow.html(val);
 
			element.css('height', Math.max($shadow[0].offsetHeight + 10 /* the "threshold" */, minHeight) + 'px');
		}
 
		element.bind('keyup keydown keypress change focus', update);
		update();
	}
});



app.config(function ($routeProvider) {
    $routeProvider
        .when('/id=:id', {
            controller: 'updateController',
            templateUrl: '/static/views/update.html',
            controllerAs: 'ctrl'
        })
        .when('/', {
            controller: 'listController',
            templateUrl: '/static/views/list.html',
            controllerAs: 'list',
            reloadOnSearch: false
        })
        .when('/Create', {
            controller: 'createController',
            templateUrl: '/static/views/create.html',
            controllerAs: 'ctrl'
        })
        .when('/CreateTemplate', {
            controller: 'createController',
            templateUrl: '/static/views/createTemplate.html',
            controllerAs: 'ctrl'
        })
        .when('/Preferences', {
            controller: 'preferencesController',
            templateUrl: '/static/views/preferences.html',
            controllerAs: 'ctrl'
        })
        .when('/groups', {
            controller: 'groupController',
            templateUrl: '/static/views/groups.html',
            controllerAs: 'ctrl'
        })
        .when('/search', {
            controller: 'searchController',
            templateUrl: '/static/views/search.html',
            controllerAs: 'list'
        })
        .otherwise({
            redirectTo: '/'
        });
});
