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

    PublicaMundi.OpenLayers.Layer.KML = PublicaMundi.Class(PublicaMundi.Layer, {
        
        getLayerExtent: function () {
            return this._layer.source_.getExtent();
        },

        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = new ol.layer.Vector({
                title: options.title,
                source: new ol.source.KML({
                    projection: options.projection,
                    url: options.url
                }),
                style: new ol.style.Style({
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color: 'rgba(255,255,255,0.4)'}),
                        radius: 5,
                        stroke: new ol.style.Stroke({
                            color: 'rgba(51,153,204, 1)',
                            width: 1.25})
                        })
                })
            });

        }
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.KML,
        framework: PublicaMundi.OpenLayers.Framework,
        type: 'PublicaMundi.Layer.KML',
        factory: PublicaMundi.OpenLayers.Layer.KML
    });

    // Add utility methods
    if (PublicaMundi.isDefined(PublicaMundi.Map)) {
        PublicaMundi.Map.prototype.KML = function (options) {
            options.type = options.type || PublicaMundi.LayerType.KML;

            this.createLayer(options);
        };
    }
})(window, window.PublicaMundi, ol);
