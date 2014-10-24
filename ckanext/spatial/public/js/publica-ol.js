var $_ = _ // keep pointer to underscore, as '_' will be overridden by a closure variable when down the stack


this.ckan.module('olpreview2', function (jQuery, _) {

    var proxy = false;

    var parseArcGisDescriptor = function(url, callback, failCallback) {

        OpenLayers.Request.GET({
            url: url,
            params: {f: "pjson"},
            success: function(request) {
                callback(JSON.parse(request.responseText))
            },
            failure: failCallback || function() {
                alert("Trouble getting ArcGIS descriptor");
                OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
            }
        });
    }

    var parseWFSCapas = function(url, callback, failCallback) {
        //console.log('wfs capas');
        //var wfsFormat = new ol.Format.WFSCapabilities();
        //var wfsFormat = 
        //console.log(wfsFormat);
        //OpenLayers.Request.GET({
        //    url: url,
        //    params: {
        //        SERVICE: "WFS",
        //        REQUEST: "GetCapabilities"
        //    },
        //    success: function(request) {
        //        var doc = request.responseXML;
        //        if (!doc || !doc.documentElement) {
        //            doc = request.responseText;
        //        }
        //        var capabilities = wfsFormat.read(doc)
        //        callback(capabilities)
        //    },
        //    failure: failCallback || function() {
        //        alert("Trouble getting capabilities doc");
        //        OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
        //    }
        //});
    }


    var parseWFSFeatureTypeDescr = function(url, ftName, ver, callback, failCallback) {
        //var format = new OpenLayers.Format.WFSDescribeFeatureType()

        //OpenLayers.Request.GET({
        //    url: url,
        //    params: {
        //        SERVICE: "WFS",
        //        REQUEST: "DescribeFeatureType",
        //        TYPENAME: ftName,
        //        VERSION: ver
        //    },
        //    success: function(request) {
         //       var doc = request.responseXML;
         //       if (!doc || !doc.documentElement) {
         //           doc = request.responseText;
         //       }
         //       var descr = format.read(doc)
         //       callback(descr)
         //   },
          //  failure: failCallback || function() {
          //      alert("Trouble getting ft decription doc");
          //      OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
          //  }
        //});
    }

    var parseWMSCapas = function(url, callback, failCallback) {
        //console.log('parseWMSCapas');
        $.ajax(url+"?request=GetCapabilities").then(function(response) {
            
            //console.log('response');
            //console.log(response);
            var capabilities = response.firstChild.getElementsByTagName("Layer");
            //console.log('capabilities');
            //console.log(capabilities);
            callback(capabilities);

        });
    }

    var createKMLLayer = function (resource) {
        var url = resource.proxy_url || resource.url

        var kml = {
                title: 'KML',
                type: PublicaMundi.LayerType.KML,
                url: url,
                click: onFeatureClick
        }

        return kml
    }

    var createGFTLayer = function (resource) {

        var tableId = parseURL(resource.url).query.docid
        return new OpenLayers.Layer.Vector(
            "GFT", {
            projection: EPSG4326,
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.Script({
                url: "https://www.googleapis.com/fusiontables/v1/query",
                params: {
                    sql: "select * from "+tableId,
                    key: CKAN_GAPI_KEY
                },
                format: new OpenLayers.Format.GeoJSON({
                    ignoreExtraDims: true,
                    read: function(json) {
                        var row, feature, atts = {}, features = [];
                        var cols = json.columns; // column names
                        for (var i = 0; i < json.rows.length; i++) {
                            row = json.rows[i];
                            feature = new OpenLayers.Feature.Vector();
                            atts = {};
                            for (var j = 0; j < row.length; j++) {
                                // 'location's are json objects, other types are strings
                                if (typeof row[j] === "object" && row[j].geometry) {
                                    feature.geometry = this.parseGeometry(row[j].geometry);
                                } else {
                                    atts[cols[j]] = row[j];
                                }
                            }
                            feature.data = atts;
                            // if no geometry, not much point in continuing with this row
                            if (feature.geometry) {
                                features.push(feature);
                            }
                        }
                        return features;
                    }
                }),
                callbackKey: "callback"
            }),
            eventListeners: {
                "featuresadded": function () {
                    this.map.zoomToExtent(this.getDataExtent());
                }
            }
        })
    }

    var createGMLLayer = function (resource) {
        var url = resource.proxy_url || resource.url

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

    var withFeatureTypesLayers = function (resource, layerProcessor) {
        //console.log('wfs');
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

        var ftLayer = { 
            name: 'test',
            title: 'Test',
            type: PublicaMundi.LayerType.WFS,
           // layer: 'osm:water_areas&bbox=-190000,-190000,200000,200000,EPSG:3857',
            layer: 'osm:water_areas&bbox=-8932736.873518838,5381166.791276408,-8922952.933898335,5390950.730896911,EPSG:3857',
            //layer: 'vae:azhistoricmines',
            url: url 
                //+'?service=WFS&' +
                //     'version=1.1.0&request=GetFeature&typename=osm:water_areas&' +
                //     'outputFormat=text/javascript&format_options=callback:loadFeatures' +
                //     '&srsname=EPSG:3857&bbox=-134.7,11.9,-45.4,60.5,EPSG:4326'
                //     '&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857'
      //          '?service=WFS&version=1.1.0&request=GetFeature&typename=WFS_transportation:Interstate&format_options=callback:loadFeatures&srsname=EPSG:3857&bbox=-117.1486,32.7025,-117.0675,32.7721',
        
        };
        console.log('ftLayer');
        console.log(ftLayer);
        var loadFeatures = function(response) {
              vectorSource.addFeatures(vectorSource.readFeatures(response));
        };
        // parseWFSCapas(
       //     url,
       //     function(capas) {

       //         var ver = capas.version
       //         if (ver == "2.0.0") ver = "1.1.0"  // 2.0.0 causes failures in some cases (e.g. Geoserver TOPP States WFS)

        //        var candidates = capas.featureTypeList.featureTypes
        //        if (ftName) candidates = candidates.filter(function(ft) {return ft.name == ftName})


       //         $_.each(candidates, function(candidate, idx) {
       //             parseWFSFeatureTypeDescr(
       //                 url,
       //                 candidate.name,
       //                 ver,
       //                 function(descr) {
       //                     if (descr.featureTypes) {
       //                         var geomProps = descr.featureTypes[0].properties.filter(function(prop) {return prop.type.startsWith("gml")})

                                // ignore feature types with no gml prop. Correct ?
       //                         if (geomProps && geomProps.length > 0) {

       //                             var ftLayer = new OpenLayers.Layer.WFSLayer(
       //                                 candidate.name, {
                                        //style: default_style,
       //                                 ftDescr: candidate,
       //                                 title: candidate.title,
       //                                 strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: MAX_FEATURES, ratio: 1})],
       //                                 projection: Mercator,
       //                                 visibility: idx==0,
       //                                 protocol: new OpenLayers.Protocol.WFS({
       //                                     headers:{"Content-Type":"application/xml; charset=UTF-8"}, // (failed) attempt at dealing with accentuated chars in some feature types
       //                                     version: ver,
       //                                     url: url,
       //                                     featureType: candidate.name,
       //                                     srsName: Mercator,
       //                                     featureNS: undefined,
       //                                     maxFeatures: MAX_FEATURES,
       //                                     geometryName: geomProps[0].name
       //                                 })
       //                             })

                                    layerProcessor(ftLayer)
       //                         }
       //                     }
       //                 }
       //             )
       //         })

       //     }
       // )
    }


    var withWMSLayers = function (resource, layerProcessor) {
        var parsedUrl = resource.url.split('#')
        var urlBody = parsedUrl[0].split('?')[0] // remove query if any
        var url = resource.proxy_service_url || urlBody

        var layerName = parsedUrl.length>1 && parsedUrl[1]

        parseWMSCapas(
            url,
            function(candidates) {
                if (layerName) candidates = candidates.filter(function(layer) {return layer.name == layerName})

                var ver = candidates.version
                $_.each(candidates, function(candidate, idx) {
                    // TODO: Need to implement this in a better way
                    var title = candidate.getElementsByTagName('Title')[0].innerHTML;
                    var name = candidate.getElementsByTagName('Name')[0].innerHTML;
                    //console.log(title);
                    //console.log(name);

                        var mapLayer = {
                        type: PublicaMundi.LayerType.WMS,
                        //candidate.name,
                        url: urlBody, // use the original URL for the getMap, as there's no need for a proxy for image request
                            transparent: true,
                           // mlDescr: candidate,
                            title: title,
                            params: {'LAYERS': name},
                       //     baseLayer: false,
                       //     singleTile: true,
                       //     visibility: idx==0,
                       //     projection: Mercator, // force SRS to 3857 if using OSM baselayer
                       //     ratio: 1
                       // }
                    //)
                    };
                    //console.log('mapLayer');
                    //console.log(mapLayer);

                    layerProcessor(mapLayer)
                })

                }
            )

    }
    
    var createGeoJSONLayer = function (resource) {
        
        var url = resource.proxy_url || resource.url
        
            var geojson = {
                title: 'GeoJson',
               // projection: ol.proj.get("EPSG:3857"), 
                type: PublicaMundi.LayerType.GeoJSON,
                url: url,
                click: onFeatureClick

        };

        //TODO add styles
        return geojson
    }


    var createEsriGeoJSONLayer = function (resource) {
        var url = resource.url

        var esrijson = new OpenLayers.Layer.Vector(
            "Esri GeoJSON",
            {
                projection: EPSG4326,
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.Script({
                    url: url, //ArcGIS Server REST GeoJSON output url
                    format: new OpenLayers.Format.EsriGeoJSON(),
                    parseFeatures: function(data) {
                        return this.format.read(data);
                    }
                })
        });

        return esrijson
    }

    var withArcGisLayers = function (resource, layerProcessor) {
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

        parseArcGisDescriptor(
            url,
            function(descriptor) {

                if (descriptor.type == "Feature Layer") {
                    var newLayer = createArcgisFeatureLayer(parsedUrl[0], descriptor, true)
                    layerProcessor(newLayer)
                } else if (descriptor.type == "Group Layer") {
                    // TODO intermediate layer
                } else if (!descriptor.type && descriptor.layers) {
                    var isFirst = true
                    $_.each(descriptor.layers, function(layer, idx) {
                        if (!layer.subLayerIds) {
                            var newLayer = createArcgisFeatureLayer(parsedUrl[0]+"/"+layer.id, layer, isFirst)
                            layerProcessor(newLayer)
                            isFirst = false
                        }})
                }

            }
        )
    }


    var createArcgisFeatureLayer = function (url, descriptor, visible) {

        var esrijson = new OpenLayers.Layer.Vector(
            descriptor.name,
            {
                projection: EPSG4326,
                strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: MAX_FEATURES, ratio: 1})],
                visibility: visible,
                protocol: new OpenLayers.Protocol.Script({
                    url: url +   //build ArcGIS Server query string
                        "/query?" +
                        //"geometry=-180%2C-90%2C180%2C90&" +
                        "geometryType=esriGeometryEnvelope&" +
                        "inSR=4326&" +
                        "spatialRel=esriSpatialRelIntersects&" +
                        "outFields=*&" +
                        "outSR=4326&" +
                        "returnGeometry=true&" +
                        "returnIdsOnly=false&" +
                        "returnCountOnly=false&" +
                        "returnZ=false&" +
                        "returnM=false&" +
                        "returnDistinctValues=false&" +
                        /*
                        "where=&" +
                        "text=&" +
                        "objectIds=&" +
                        "time=&" +
                        "relationParam=&" +
                        "maxAllowableOffset=&" +
                        "geometryPrecision=&" +
                        "orderByFields=&" +
                        "groupByFieldsForStatistics=&" +
                        "outStatistics=&" +
                        "gdbVersion=&" +
                        */
                        "f=pjson",
                    format: new OpenLayers.Format.EsriGeoJSON(),
                    maxFeatures: 1000,
                    parseFeatures: function(data) {
                        return this.format.read(data);
                    },
                    filterToParams: function(filter, params) {
                        var format = new OpenLayers.Format.QueryStringFilter({srsInBBOX: this.srsInBBOX})
                        var params = format.write(filter, params)
                        params.geometry = params.bbox
                        delete params.bbox

                        return params
                    }
                })
            });

        return esrijson
    }

    var layerExtractors = {
        'kml': function(resource, layerProcessor) {layerProcessor(createKMLLayer(resource))},
        'gml': function(resource, layerProcessor) {layerProcessor(createGMLLayer(resource))},
        'geojson': function(resource, layerProcessor) {layerProcessor(createGeoJSONLayer(resource))},
        'wfs': withFeatureTypesLayers,
        'wms': withWMSLayers,
        'esrigeojson': function(resource, layerProcessor) {layerProcessor(createEsriGeoJSONLayer(resource))},
        'arcgis_rest': withArcGisLayers,
        'gft': function(resource, layerProcessor) {layerProcessor(createGFTLayer(resource))}
    }

 
    var withLayers = function(resource, layerProcessor) {
        var resourceUrl = resource.url
        var proxiedResourceUrl = resource.proxy_url
        var proxiedServiceUrl = resource.proxy_service_url

        var withLayers = layerExtractors[resource.format && resource.format.toLocaleLowerCase()]
        withLayers && withLayers(resource, layerProcessor)
    }

    var onFeatureClick = function (features) {
            alert(JSON.stringify(features));
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

        addLayer: function(resourceLayer) {
            
            console.log('layer opts=');
            console.log(resourceLayer);
            var layer = this.map.createLayer(resourceLayer);
            console.log('layer=');
            console.log(layer);
            //this.map.setExtent(layer.getLayerExtent()); 
            layer.addToControl();

           
        //this.map.setExtent(layer_extent);
                        //var bbox = resourceLayer.getDataExtent && resourceLayer.getDataExtent()
            //if (bbox) {
            //    if (this.map.getExtent()) this.map.getExtent().extend(bbox)
            //    else this.map.zoomToExtent(bbox)
           // }
           // else {
           //     var firstExtent = false
           //     resourceLayer.events.register(
           //         "loadend",
           //         resourceLayer,
           //         function(e) {
           //             if (!firstExtent) {
           //                 var bbox = e && e.object && e.object.getDataExtent && e.object.getDataExtent()
           //                 if (bbox)
           //                     if (this.map.getExtent()) this.map.getExtent().extend(bbox)
           //                     else this.map.zoomToExtent(bbox)
           //                 else
           //                     this.map.zoomToMaxExtent()
           //                 firstExtent = true
           //             }
           //         })
           // }

        },

        _onReady: function () {

            var mapDiv = $("<div></div>").attr("id", "map-ol").addClass("map")
            var info = $("<div></div>").attr("id", "info2")
            mapDiv.append(info)

            $("#data-preview2").empty()
            $("#data-preview2").append(mapDiv)

            PublicaMundi.noConflict();
            
            var baseLayers = [{
                        title: 'Open Street Maps',
                        type: PublicaMundi.LayerType.TILE,
                        url: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        }];

            var options = {
                target: 'map-ol',
                center: [50, 100],
                zoom: 2,
                layers: baseLayers,
                minZoom: 2,
                maxZoom: 17,
            };
            this.map = PublicaMundi.map(options);
            
            this.map.setLayerControl(this.map.getLayers()[0]);
            
            withLayers(preload_resource, $_.bind(this.addLayer, this))
            //this.map.setExtent();
        }
    }
});
