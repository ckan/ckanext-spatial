/// <reference path="../PublicaMundi.js" />
(function (window, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers');

    PublicaMundi.OpenLayers.Layer = PublicaMundi.Class(PublicaMundi.Layer, {
        test: function() {
            console.log( 'this is a test!');
        }
    });
    //}
    //);

    PublicaMundi.locator.register('PublicaMundi.OpenLayers.Layer', PublicaMundi.OpenLayers.Layer);
})(window, window.PublicaMundi, ol);
