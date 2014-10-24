/// <reference path="../PublicaMundi.js" />
(function (window, PublicaMundi, L) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof L === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Leaflet');

    PublicaMundi.Leaflet.Layer = PublicaMundi.Class(PublicaMundi.Layer, {
        test: function() {
            console.log( 'this is a test!');
        }
    });

    PublicaMundi.locator.register('PublicaMundi.Leaflet.Layer', PublicaMundi.Leaflet.Layer);
})(window, window.PublicaMundi, L);
