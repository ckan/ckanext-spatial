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
                "fillOpacity":0.4
//            "pointRadius":7
            }
        },

        setup: function(){
            if (!this.extent)
                return false;

            // Setup some sizes
            var width = $(CKAN.DatasetMap.element).width();
            if (width > 1024) {
                width = 1024;
            }
            var height = ($(CKAN.DatasetMap.element).height() || width/2);
            $("#dataset-map-container").width(width);
            $("#dataset-map-container").height(height);

            if (this.map_type=='osm') {
                var mapquestTiles = [
                    "http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                    "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                    "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                    "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"];

                var layers = [
                  new OpenLayers.Layer.OSM("MapQuest-OSM Tiles", mapquestTiles)
                ];

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
                        new OpenLayers.Control.PanZoom(),
                        new OpenLayers.Control.Navigation()
                    ],
                    "theme":"/ckanext/spatial/js/openlayers/theme/default/style.css"
                });
                var internalProjection = new OpenLayers.Projection("EPSG:900913");
            } else if (this.map_type=='os') {

                var copyrightStatements = "Contains Ordnance Survey data (c) Crown copyright and database right  [2012] <br>" + "Contains Royal Mail data (c) Royal Mail copyright and database right [2012]<br>" + "Contains bathymetry data by GEBCO (c) Copyright [2012]<br>" + "Contains data by Land & Property Services (Northern Ireland) (c) Crown copyright [2012]";

                // Create a new map
                var layers = [
                  new OpenLayers.Layer.WMS("Geoserver layers - Tiled",
			'http://osinspiremappingprod.ordnancesurvey.co.uk/geoserver/gwc/service/wms', {
                        LAYERS: 'InspireETRS89',
		        STYLES: '',
		        format: 'image/png',
		        tiled: true
                        }, {
		        buffer: 0,
		        displayOutsideMaxExtent: true,
		        isBaseLayer: true,
		        attribution: copyrightStatements,
                        transitionEffect: 'resize'
                        }
                  )
                ];
                OpenLayers.DOTS_PER_INCH = 90.71428571428572;

    		var options = {
			        size: new OpenLayers.Size(width, height),
                                scales: [15000000, 10000000, 5000000, 1000000, 250000, 75000],
			        maxExtent: new OpenLayers.Bounds(-30, 48.00, 3.50, 64.00),
			        restrictedExtent: new OpenLayers.Bounds(-30, 48.00, 3.50, 64.00),
			        tileSize: new OpenLayers.Size(250, 250),
			        units: 'degrees',
			        projection: "EPSG:4258"
    		};

                this.map = new OpenLayers.Map("dataset-map-container", {});

	        // Set the options on the map
		this.map.setOptions(options);

                var internalProjection = new OpenLayers.Projection("EPSG:4258");
            }
            this.map.addLayers(layers);
            
            var geojson_format = new OpenLayers.Format.GeoJSON({
                "internalProjection": internalProjection,
                "externalProjection": new OpenLayers.Projection("EPSG:4326")
            });

            // Add the Dataset Extent box
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

