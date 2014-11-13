(function (global, PublicaMundi, L) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof L === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Leaflet.Layer');

    PublicaMundi.Leaflet.Layer.Tile = PublicaMundi.Class(PublicaMundi.Layer, {
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = L.tileLayer(options.url);
        },
        addToControl: function() { 
            this.getMap()._getLayerControl().addBaseLayer(this._layer, this._options.title);
        },

    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.TILE,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.Tile',
        factory: PublicaMundi.Leaflet.Layer.Tile
    });
})(window, window.PublicaMundi, L);
