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

    PublicaMundi.OpenLayers.Layer.WFS = PublicaMundi.Class(PublicaMundi.OpenLayers.Layer, {
        getLayerExtent: function () {
            return this._layer.source_.getExtent();
        },
       
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);
            console.log('options');
            console.log(options);
            this._map = null;
            this._type = null;
            this._layer = new ol.layer.Vector({
                title: options.title,
                source: new ol.source.ServerVector({
                    format: new ol.format.GeoJSON(),
                    loader: function(extent, resolution, projection) {
                        $.ajax({
                            url: options.url,
                            dataType: 'jsonp',
                        
                           //loadFeatures : function(response) {
                           //  this._layer.addFeatures(vectorSource.readFeatures(response));
                           //    }

                        } );
                //.then( function(response){
                //            console.log('then ');
                //            console.log(response);
                        //var loadFeatures = function(response) {
                        //    this._layer.addFeatures(this._layer.readFeatures(response));
                        //    };

                  //      });
                    },
                //addFeatures: response,
                strategy: ol.loadingstrategy.createTile(new ol.tilegrid.XYZ({
                    maxZoom: 19
                })),
                projection: 'EPSG:3857'
                })
            });

            
                //source: new ol.source.TileWS({
                //    url: options.url,
                //    params: options.params
                //})
          //  });
        }
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.WFS,
        framework: PublicaMundi.OpenLayers.Framework,
        type: 'PublicaMundi.Layer.WFS',
        factory: PublicaMundi.OpenLayers.Layer.WFS
    });
})(window, window.PublicaMundi, ol);
