/// <reference path="../../OpenLayers/build/ol-whitespace.js" />

/// <reference path="../../PublicaMundi.js" />
/// <reference path="../Layer.js" />

(function (global, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers.Layer');

    PublicaMundi.OpenLayers.Layer.GeoJson = PublicaMundi.Class(PublicaMundi.Layer, {
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = new ol.layer.Vector({
                title: options.title,
                source: new ol.source.GeoJSON({
                    projection: options.projection,
                    url: options.url
                }),
            });
           },
        setLayerExtent: function() {
            var layer = this;
            this._layer.once('postcompose', function() {
                layer._extent = this.getSource().getExtent();
                layer.getMap().setExtent(layer._extent, 'EPSG:3857');
            });
        },
        
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.GeoJSON,
        framework: PublicaMundi.OpenLayers.Framework,
        type: 'PublicaMundi.Layer.GeoJson',
        factory: PublicaMundi.OpenLayers.Layer.GeoJson
    });

    // Add utility methods
    if (PublicaMundi.isDefined(PublicaMundi.Map)) {
        PublicaMundi.Map.prototype.geoJSON = function (options) {
            options.type = options.type || PublicaMundi.LayerType.GeoJSON;

            this.createLayer(options);
        };
    }
})(window, window.PublicaMundi, ol);
