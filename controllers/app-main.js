var app = angular.module('module1', ['ngRoute', 'ngGrid', 'ui.bootstrap', 'ngTagsInput']);

//
// Main Controller
//
app.controller('main', function ($http, $scope) {
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
            controllerAs: 'list'
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
