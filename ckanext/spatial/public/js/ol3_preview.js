// Openlayers preview module
this.ckan.module('olpreview', function (jQuery, _) {

    var proxy = false;

    var createKMLLayer = function (url) {
        var kml = new ol.layer.Vector({
            source: new ol.source.Vector({
                parser: new ol.parser.KML({
                    maxDepth: 1, extractStyles: true, extractAttributes: true
                }),
                url: url
            })
        });

        return kml
    }

    var createGMLLayer = function (url) {
        var gml = new ol.layer.Vector({
            source: new ol.source.Vector({
                parser: new ol.parser.ogc.GML_v3(),
                url: url
            }),
            style: new ol.style.Style({
                symbolizers: [
                    new ol.style.Fill({
                        color: '#ffffff',
                        opacity: 0.25
                    }),
                    new ol.style.Stroke({
                        color: '#6666ff'
                    })
                ]
            })
        })

        return gml
    }

    var createGeoJSONLayer = function (url) {
        var geojson = new ol.layer.Vector({
            source: new ol.source.Vector({
                parser: new ol.parser.GeoJSON(),
                url: url
            }),
            style: new ol.style.Style({rules: [
                new ol.style.Rule({
                    symbolizers: [
                        new ol.style.Fill({
                            color: 'white',
                            opacity: 0.6
                        }),
                        new ol.style.Stroke({
                            color: '#6666ff',
                            opacity: 1
                        })
                    ]
                }),
                new ol.style.Rule({
                    maxResolution: 5000,
                    symbolizers: [
                        new ol.style.Text({
                            color: 'black',
                            text: ol.expr.parse('name'),
                            fontFamily: 'Calibri,sans-serif',
                            fontSize: 12,
                            stroke: new ol.style.Stroke({
                                color: 'white',
                                width: 3
                            })
                        })
                    ]
                })
            ]})
        });

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
            var basemapLayer = new ol.layer.Tile({
                source: new ol.source.MapQuestOpenAerial()
            })

            var mapDiv = $("<div></div>").attr("id", "map").addClass("map")
            var info = $("<div></div>").attr("id", "info")
            mapDiv.append(info)

            $("#data-preview").empty()
            $("#data-preview").append(mapDiv)

            info.tooltip({
                animation: false,
                trigger: 'manual'
            });

            var map = new ol.Map({
                target: 'map',
                layers: [basemapLayer, resourceLayer],
                renderer: ol.RendererHint.CANVAS,
                view: new ol.View2D({
                    center: ol.proj.transform([37.41, 8.82], 'EPSG:4326', 'EPSG:3857'),
                    zoom: 4
                })
            });

            $(map.getViewport()).on('mousemove', function(evt) {
                var pixel = map.getEventPixel(evt.originalEvent);
                displayFeatureInfo(map, resourceLayer, info, pixel);
            });

            map.on('singleclick', function(evt) {
                var pixel = evt.getPixel();
                displayFeatureInfo(map, resourceLayer, info, pixel);
            });
        }
    }
});


