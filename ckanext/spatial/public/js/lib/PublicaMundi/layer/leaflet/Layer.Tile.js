/// <reference path="../../../Leaflet/leaflet-src.js" />

/// <reference path="../../PublicaMundi.js" />
/// <reference path="../Layer.js" />

(function (global, PublicaMundi, L) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof L === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Leaflet.Layer');

    PublicaMundi.Leaflet.Layer.Tile = PublicaMundi.Class(PublicaMundi.Leaflet.Layer, {
        addToControl: function() { 
            console.log('adding?');
            this._map.getLayerControl().addBaseLayer(this._layer, this._options.title);
        },

        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = L.tileLayer(options.url);
            
        }
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.TILE,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.Tile',
        factory: PublicaMundi.Leaflet.Layer.Tile
    });

})(window, window.PublicaMundi, L);
