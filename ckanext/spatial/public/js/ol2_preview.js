// Openlayers preview module
this.ckan.module('olpreview', function (jQuery, _) {

    var proxy = false;

    var createKMLLayer = function (url) {
        var kml = new OpenLayers.Layer.Vector("KML", {
            projection: "EPSG:4326",
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: url,
                format: new OpenLayers.Format.KML({
                    extractStyles: true,
                    extractAttributes: true,
                    maxDepth: 2
                })
            })
        })

        return kml
    }

    var createGMLLayer = function (url) {
        var gml = new OpenLayers.Layer.Vector("GML", {
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: url,
                format: new OpenLayers.Format.GML()
            })
        });

        //TODO styles

        return gml
    }

    var createGeoJSONLayer = function (url) {

        var geojson = new OpenLayers.Layer.Vector(
            "GeoJSON",
            {
                projection: "EPSG:4326",
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: url,
                    format: new OpenLayers.Format.GeoJSON()
            })
        });

        //TODO add styles

        return geojson
    }

    layerConstructors = {
        'kml': createKMLLayer,
        'gml': createGMLLayer,
        'geojson': createGeoJSONLayer
    }

    var createLayer = function (resource) {
        var resourceUrl = resource.url
        var proxiedResourceUrl = resource.proxy_url

        var cons = layerConstructors[resource.format && resource.format.toLocaleLowerCase()]
        return cons && cons(proxiedResourceUrl || resourceUrl)
    }


    var displayFeatureInfo = function(map, layer, info, pixel) {
        info.css({
            left: pixel[0] + 'px',
            top: (pixel[1] - 15) + 'px'
        });
        map.getFeatures({
            pixel: pixel,
            layers: [layer],
            success: function(layerFeatures) {
                var feature = layerFeatures[0][0];
                if (feature) {
                    info.tooltip('hide')
                        .attr('data-original-title', feature.get('name'))
                        .tooltip('fixTitle')
                        .tooltip('show');
                } else {
                    info.tooltip('hide');
                }
            }
        });
    };

    return {
        options: {
            i18n: {
            }
        },

        initialize: function () {
            jQuery.proxyAll(this, /_on/);
            this.el.ready(this._onReady);
        },

        _onReady: function () {

            var resourceLayer = createLayer(preload_resource)
            var basemapLayer = new OpenLayers.Layer.OSM( "Simple OSM Map")

            var mapDiv = $("<div></div>").attr("id", "map").addClass("map")

            $("#data-preview").empty()
            $("#data-preview").append(mapDiv)

            resourceLayer.events.register(
                "loadend",
                resourceLayer,
                function(e) {
                    var bbox = e && e.object && e.object.getDataExtent && e.object.getDataExtent()
                    if (bbox) map.zoomToExtent(bbox)
                    else map.zoomToMaxExtent()
                })

            var map = new OpenLayers.Map(
                {
                    div: "map",
                    layers: [basemapLayer, resourceLayer],
                    zoom: 4,
                    eventListeners: {
                        featureover: function(e) {
                            e.feature.renderIntent = "select";
                            e.feature.layer.drawFeature(e.feature);
                            //log("Map says: Pointer entered " + e.feature.id + " on " + e.feature.layer.name);
                        },
                        featureout: function(e) {
                            e.feature.renderIntent = "default";
                            e.feature.layer.drawFeature(e.feature);
                            //log("Map says: Pointer left " + e.feature.id + " on " + e.feature.layer.name);
                        },
                        featureclick: function(e) {
                            //log("Map says: " + e.feature.id + " clicked on " + e.feature.layer.name);
                        }
                    }
                });

            /*
                map.setCenter(new OpenLayers.LonLat(-71.147, 42.472).transform(
                new OpenLayers.Projection("EPSG:4326"),
                map.getProjectionObject()
            ))
            */

        }
    }
});


