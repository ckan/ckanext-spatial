(function (window, PublicaMundi) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi');

    PublicaMundi.Layer = PublicaMundi.Class({
        initialize: function (options) {

            this._map = null;
            this._type = null;
            this._layer = null;
            this._extent = options.bbox || null;
            this._options = options || {};
        },
        setMap: function(map) {
            this._map = map;
        },
        getMap: function() {
            return this._map;
        },
        getType: function() {
            return this._type;
        },
        getLayer: function () {
            return this._layer;
        },
        setLayerExtent: function() {
            return this._extent;
        },
        getOptions: function () {
            return this._options;
        },
        addToControl: function() { 
            return null;
        },
        update: function() {
            return null;
        },

    });

    PublicaMundi.locator.register('PublicaMundi.Layer', PublicaMundi.Layer);
})(window, PublicaMundi);
