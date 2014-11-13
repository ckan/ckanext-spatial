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

    PublicaMundi.Leaflet.Layer.KML = PublicaMundi.Class(PublicaMundi.Layer, {
        setLayerExtent: function() {
            var layer = this;
            var extent = [-180,-90,180,90];
            this._layer.on('layeradd', function() {
                var currextent = this.getBounds();
                var southWest = currextent.getSouthWest();
                var northEast = currextent.getNorthEast();
                
                var minx = extent[0];
                var miny = extent[1];
                var maxx = extent[2];
                var maxy = extent[3];
                
                if (southWest.lng > extent[0]) {
                    minx = southWest.lng;
                }
                if (southWest.lat > extent[1]) {
                    miny = southWest.lat;
                }
                if (northEast.lng < extent[2]) {
                    maxx = northEast.lng;
                }
                if (northEast.lat < extent[3]) {
                    maxy = northEast.lat;
                }
                layer._extent = [minx, miny, maxx, maxy];

                layer._map.setExtent(layer._extent, 'EPSG:4326');
            });
        },

        addToControl: function() { 

            this.getMap()._getLayerControl().addOverlay(this._layer, this._options.title);
            },
 
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            if (!PublicaMundi.isDefined(options.projection)) {
                // TODO : Resolve projection / reproject    
            }

            var onClick = null;
            if (PublicaMundi.isFunction(options.click)) {
                onClick = function (e) {
                    options.click([e.target.feature.properties], [e.latlng.lat * (6378137), e.latlng.lng* (6378137)]);
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
                },
                onEachFeature: function onEachFeature(feature, layer) {
                    if (PublicaMundi.isFunction(onClick)) {
                        layer.on({
                            click: onClick
                        });
                    }
                },
         
            
               async: true,
                    });

            $.ajax({
                type: "GET",
                url: options.url,
                dataType: 'xml',
                context: this,
                success: function (response) {
                    // Converting KML to geojson and handling as json
                    var test = toGeoJSON.kml(response);
                    this._layer.addData(test);
                }
            });
        }
    });
    
    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.KML,
        framework: PublicaMundi.Leaflet.Framework,
        type: 'PublicaMundi.Layer.KML',
        factory: PublicaMundi.Leaflet.Layer.KML
    });

    // Add utility methods
    if (PublicaMundi.isDefined(PublicaMundi.Map)) {
        PublicaMundi.Map.prototype.KML = function (options) {
            //console.log('helper?');
            switch (typeof options) {

            }
            options.type = options.type || PublicaMundi.LayerType.KML;

            this.createLayer(options);
        };
    }
})(window, window.PublicaMundi, L, jQuery);
