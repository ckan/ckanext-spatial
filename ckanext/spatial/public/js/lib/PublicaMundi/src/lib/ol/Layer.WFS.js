/// <reference path="../../OpenLayers/build/ol-whitespace.js" />

/// <reference path="../../PublicaMundi.js" />
/// <reference path="../../PublicaMundi.OpenLayers.js" />
/// <reference path="../Layer.js" />

(function (window, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers.Layer');

    PublicaMundi.OpenLayers.Layer.WFS = PublicaMundi.Class(PublicaMundi.Layer, {
        update: function() {
                    },
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);
            this._map = null;
            this._type = null;
            var vectorSource = new ol.source.ServerVector({
                    format: new ol.format.GeoJSON(),
                    //format: new ol.format.GML(),
                    projection: options.projection,
                     loader: function(extent, resolution, projection) {
                        $.ajax({
                           // type: "GET",
                            url: options.url+ '&bbox=' + extent.join(',')+ ',EPSG:3857 ',
                            //'&format_options=callback:loadFeatures',
                            //dataType: 'jsonp',
                            dataType: 'json',
                            //dataType: 'gml',
                            context: this,
                            success: function(response) {
                                //console.log('SUCCESS');
                                //console.log(response);
                                loadFeatures(response);
                            },
                            failure: function(response) {
                                //console.log('FAILURE');
                                //console.log(response);
                            }
                        } )

                     },
            });

            var loadFeatures = function(response) {
                vectorSource.addFeatures(vectorSource.readFeatures(response));
                }

            this._layer = new ol.layer.Vector({
                title: options.title,
                source: vectorSource, 
                visible: options.visible,
                strategy: ol.loadingstrategy.createTile(new ol.tilegrid.XYZ({
                    maxZoom: 19,
                    //minZoom: 8
                })),
                //projection: 'EPSG:4326'
               // })
            });
        
        
            
        },
        setLayerExtent: function() {
            var layer = this;
            this._layer.once('postcompose', function() {
                layer.getMap().setExtent(layer._extent, 'EPSG:4326');
            });
        },
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.WFS,
        framework: PublicaMundi.OpenLayers.Framework,
        type: 'PublicaMundi.Layer.WFS',
        factory: PublicaMundi.OpenLayers.Layer.WFS
    });
})(window, window.PublicaMundi, ol);
