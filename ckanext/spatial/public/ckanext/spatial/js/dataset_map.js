var CKAN = CKAN || {};

CKAN.DatasetMap = function($){

    // Private
    
    var getGeomType = function(feature){
        return feature.geometry.CLASS_NAME.split(".").pop().toLowerCase()
    }

    var getStyle = function(geom_type){
        var styles = CKAN.DatasetMap.styles;
        var style = (styles[geom_type]) ? styles[geom_type] : styles["default"];

        return new OpenLayers.StyleMap(OpenLayers.Util.applyDefaults(
                    style, OpenLayers.Feature.Vector.style["default"]))
    }

    // Public
    return {
        map: null,

        extent: null,

        styles: {
            "point":{
                "externalGraphic": "/ckanext/spatial/marker.png",
                "graphicWidth":14,
                "graphicHeight":25,
                "fillOpacity":1
            },
            "default":{
//            "fillColor":"#ee9900",
                "fillColor":"#FCF6CF",
                "strokeColor":"#B52",
                "strokeWidth":2,
                "fillOpacity":0.4,
//            "pointRadius":7
            }
        },

        setup: function(){
            if (!this.extent)
                return false;

            // Setup some sizes
            var w = $("#dataset").width();
            if (w > 1024) w = 1024;
            $("#dataset-map-container").width(w);
            $("#dataset-map-container").height(w/3);


            var layers = [
                new OpenLayers.Layer.OSM()
            ]


            // Create a new map
            this.map = new OpenLayers.Map("dataset-map-container" ,
                {
                "projection": new OpenLayers.Projection("EPSG:900913"),
                "displayProjection": new OpenLayers.Projection("EPSG:4326"),
                "units": "m",
                "numZoomLevels": 18,
                "maxResolution": 156543.0339,
                "maxExtent": new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508.34),
                "controls": [ 
                    new OpenLayers.Control.Attribution(),
                    new OpenLayers.Control.PanZoom(),
                    new OpenLayers.Control.Navigation()
                ],
                "theme":"/ckanext/spatial/js/openlayers/theme/default/style.css"
            });
            this.map.addLayers(layers);
            
            var geojson_format = new OpenLayers.Format.GeoJSON({
                "internalProjection": new OpenLayers.Projection("EPSG:900913"),
                "externalProjection": new OpenLayers.Projection("EPSG:4326")
            });
            var features = geojson_format.read(this.extent)
            var geom_type = getGeomType(features[0])

            var vector_layer = new OpenLayers.Layer.Vector("Dataset Extent",
                {
                    "projection": new OpenLayers.Projection("EPSG:4326"),
                    "styleMap": getStyle(geom_type)
                }
            ); 
            
            this.map.addLayer(vector_layer);
            vector_layer.addFeatures(features);
            if (geom_type == "point"){
                this.map.setCenter(new OpenLayers.LonLat(features[0].geometry.x,features[0].geometry.y),
                                   this.map.numZoomLevels/2)
            } else {
                this.map.zoomToExtent(vector_layer.getDataExtent()); 
            }
        }
    }
}(jQuery)


OpenLayers.ImgPath = "/ckanext/spatial/js/openlayers/img/";

