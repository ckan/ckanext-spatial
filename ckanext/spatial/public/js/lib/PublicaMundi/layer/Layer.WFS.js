/// <reference path="../../OpenLayers/build/ol-whitespace.js" />

/// <reference path="../PublicaMundi.js" />
/// <reference path="../Layer.js" />

(function (global, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Layer');

    PublicaMundi.Layer.WFS = function (options) {
        this._map = options._map;

        options.type = options.type || PublicaMundi.LayerType.WFS;

        this._layer = PublicaMundi.registry.createLayer(options);

        this.getLayer = function () {
            return this._layer;
        };
    };

    PublicaMundi.locator.register('PublicaMundi.Layer.WFS', PublicaMundi.Layer.WFS);
})(window, window.PublicaMundi, ol);
