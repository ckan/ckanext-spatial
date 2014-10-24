/// <reference path="../../../jQuery/jquery-2.1.0.intellisense.js" />
/// <reference path="../../../Leaflet/leaflet-src.js" />

/// <reference path="../../PublicaMundi.js" />
/// <reference path="../Layer.js" />

(function (global, PublicaMundi, L, $) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof L === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Leaflet.Layer');

    PublicaMundi.Leaflet.Layer.GeoJson = PublicaMundi.Class(PublicaMundi.Leaflet.Layer, {
        addToControl: function() { 
            this._map.getLayerControl().addOverlay(this._layer, this._options.title);
            },
        getLayerExtent: function () {
            return this._layer.getBounds();
        },

        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            if (!PublicaMundi.isDefined(options.projection)) {
                // TODO : Resolve projection / reproject    
            }

            var onClick = null;
            if (PublicaMundi.isFunction(options.click)) {
                onClick = function (e) {
                    options.click([e.target.feature.properties]);
                };
            }
            this._layer = L.geoJson(null, {
                style: {
                    color: '#3399CC',
                    weight: 1.25,
                    opacity: 1,
                    fillColor: '#FFFFFF',
                    fillOpacity: 0.4
                }, pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, {
                        radius: 5,
                        fillColor: '#FFFFFF',
                        fillOpacity: 0.4,
                        color: "#3399CC",
                        weight: 1.25,
                        opacity: 1
                    });
                }, onEachFeature: function onEachFeature(feature, layer) {
                    if (PublicaMundi.isFunction(onClick)) {
                        layer.on({
                            click: onClick
                        });
                    }
                }
            });

            $.ajax({
                type: "GET",
                url: options.url,
                dataType: 'json',
                context: this,
                success: function (response) {
                    this._layer.addData(response);
                }
            });
        },

    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.GeoJSON,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.GeoJson',
        factory: PublicaMundi.Leaflet.Layer.GeoJson
    });

    // Add utility methods
    if (PublicaMundi.isDefined(PublicaMundi.Map)) {
        PublicaMundi.Map.prototype.geoJSON = function (options) {
            switch (typeof options) {

            }
            options.type = options.type || PublicaMundi.LayerType.GeoJSON;

            this.createLayer(options);
        };
    }
})(window, window.PublicaMundi, L, jQuery);
