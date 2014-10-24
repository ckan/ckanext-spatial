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

    PublicaMundi.Leaflet.Layer.WMS = PublicaMundi.Class(PublicaMundi.Leaflet.Layer, {
        addToControl: function() { 
            //console.log(this._layer);
            var map = this._map;
            var title = this._options.title;
            this._map._map.on('layeradd', function(e) {
                map.getLayerControl().addOverlay(e.layer, title);
            });
            },
        
        getLayerExtent: function () {
            return this._layer.getBounds();
        },

        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = L.tileLayer.wms(options.url, {
                layers: options.params.LAYERS,
                format: 'image/png',
                transparent: true
            });
        },
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.WMS,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.WMS',
        factory: PublicaMundi.Leaflet.Layer.WMS
    });
})(window, window.PublicaMundi, L);
