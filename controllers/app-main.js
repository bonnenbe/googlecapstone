var app = angular.module('module1', ['ngRoute', 'ngGrid', 'ui.bootstrap', 'ngTagsInput']);

//
// Main Controller
//
app.controller('main', function ($http, $scope) {
    $http.get('/user').success(function (data) {
        $scope.user = data.user;
        $scope.inAdmins = data.inAdmins;
        $scope.inCommittee = data.inCommittee;
    });
    $scope.onEnter = function (event, foo) {
        if (event.which == 13)
            foo.call();
    };
});


app.config(function ($routeProvider) {
    $routeProvider
        .when('/id=:id', {
            controller: 'updateController',
            templateUrl: '/views/update.html',
            controllerAs: 'ctrl'
        })
        .when('/', {
            controller: 'listController',
            templateUrl: '/views/list.html',
            controllerAs: 'list'
        })
        .when('/Create', {
            controller: 'createController',
            templateUrl: '/views/create.html',
            controllerAs: 'ctrl'
        })
        .when('/groups', {
            controller: 'groupController',
            templateUrl: '/views/groups.html',
            controllerAs: 'ctrl'
        })
        .when('/search', {
            controller: 'searchController',
            templateUrl: '/views/search.html',
            controllerAs: 'list'
        })
        .otherwise({
            redirectTo: '/'
        });
});
