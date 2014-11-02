// <reference path="../../../jQuery/jquery-2.1.0.intellisense.js" />
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

    PublicaMundi.Leaflet.Layer.GeoJson = PublicaMundi.Class(PublicaMundi.Layer, {
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
                //url: 'http://83.212.98.90:5000/dataset/hello-foo-2/resource/5c77af59-f964-4f25-8685-fd2e4b853867/service_proxy?service=WFS&version=1.1.0&request=GetFeature&typename=osm:water_areas&outputFormat=json&srsname=EPSG:3857&bbox=-8901397.691921914,5403868.588677103,-8833521.610804677,5434443.399991176 ,EPSG:3857',
                //url: 'http://83.212.98.90:5000/dataset/hello-foo-2/resource/5c77af59-f964-4f25-8685-fd2e4b853867/service_proxy?service=WFS&version=1.1.0&request=GetFeature&typename=osm:polygon_barrier&outputFormat=json&srsname=EPSG:3857&bbox=-8904760.921166463,5403639.277592248,-8836884.840049226,5434214.088906321,EPSG:3857',
                dataType: 'json',
                context: this,
                success: function (response) {
                    //console.log('response');
                    //console.log(response);
                    this._layer.addData(response);
                    //console.log('layer');
                    //console.log(this._layer);
                    //this.addToControl();
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
