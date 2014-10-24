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

    PublicaMundi.Leaflet.Layer.WFS = PublicaMundi.Class(PublicaMundi.Leaflet.Layer, {
        addToControl: function() { 
            console.log(this._layer);
            var map = this._map;
            var title = this._options.title;
            this._map._map.on('layeradd', function(e) {
                //console.log('LAYER READY');
                //console.log(e);
                map.getLayerControl().addOverlay(e.layer, title);
            });
            },
        
        getLayerExtent: function () {
            return this._layer.getBounds();
        },

        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);
            
            this._layer = new L.GeoJSON.WFS(options.url, options.layer, {
                    pointToLayer: function(latlng) { return new L.CircleMarker(latlng) },
                    hoverFld: "name"
            });
        }
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.WFS,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.WFS',
        factory: PublicaMundi.Leaflet.Layer.WFS
    });
})(window, window.PublicaMundi, L);
