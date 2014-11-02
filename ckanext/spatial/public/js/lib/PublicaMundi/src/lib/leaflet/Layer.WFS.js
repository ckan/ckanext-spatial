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

    PublicaMundi.Leaflet.Layer.WFS = PublicaMundi.Class(PublicaMundi.Layer, {
        addToControl: function() {
            var map = this._map;
            var title = this._options.title;
            this._map._map.on('layeradd', function(e) {

                map.getLayerControl().addOverlay(e.layer, title);
            });
        },
        
        getLayerExtent: function () {
            return this._layer.getBounds();
        },
        update: function() { 
            var bbox = this._map.getViewBox();
            $.ajax({
                type: "GET",
                url: this._options.url+ '&bbox=' + bbox + ',EPSG:3857',
                dataType: 'json',
                context: this,
                success: function (response) {
                    console.log('SUCCESS');
                    console.log('response');
                    //console.log(response);
                    this._layer.clearLayers();
                    this._layer.addData(response);
                    console.log('layer');
                    console.log(this._layer);
                }
            });
        },
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);
            
            this._bbox = options.bbox;
            var onClick = null;
            if (PublicaMundi.isFunction(options.click)) {
                onClick = function (e) {
                    options.click([e.target.feature.properties]);
                };
            };
            this._layer = L.geoJson(null, {
                style: {
                    color: '#3399CC',
                    weight: 1.25,
                    opacity: 1,
                    fillColor: '#FFFFFF',
                    fillOpacity: 0.4
                }, 
                    pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, {
                        radius: 5,
                        fillColor: '#FFFFFF',
                        fillOpacity: 0.4,
                        color: "#3399CC",
                        weight: 1.25,
                        opacity: 1
                    });
                }, 

                visible: options.visible,
                onEachFeature: function onEachFeature(feature, layer) {
                    if (PublicaMundi.isFunction(onClick)) {
                        layer.on({
                            click: onClick
                        });
                    }

                }
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
