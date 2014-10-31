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
        $.ajax(url+"?request=GetCapabilities").then(function(response) {
            
            
            //console.log('wfs capas');
            var capabilities = response.firstChild.getElementsByTagName("FeatureType");
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

            }

    var createGMLLayer = function (resource) {
        var url = resource.proxy_url || resource.url

        //var gml = new OpenLayers.Layer.Vector("GML", {
        //    strategies: [new OpenLayers.Strategy.Fixed()],
        //    protocol: new OpenLayers.Protocol.HTTP({
        //        url: url,
        //        format: new OpenLayers.Format.GML()
        //    })
        //});

        //TODO styles

        //return gml
    }

    var withFeatureTypesLayers = function (resource, layerProcessor) {
        //console.log('wfs');
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

        parseWFSCapas(
            url,
            function(candidates) {

                $_.each(candidates, function(candidate, idx) {
                    // TODO: Need to implement this in a better way
                    var title = candidate.getElementsByTagName('Title')[0].innerHTML;
                    var name = candidate.getElementsByTagName('Name')[0].innerHTML;
                    var bbox = candidate.getElementsByTagName('WGS84BoundingBox')[0];
                    var lc = bbox.getElementsByTagName('LowerCorner')[0].innerHTML;
                    var uc = bbox.getElementsByTagName('UpperCorner')[0].innerHTML;
                    lc = lc.split(' ');
                    uc = uc.split(' ');
                    var bboxfloat = [ parseFloat(lc[0]), parseFloat(lc[1]), parseFloat(uc[0]), parseFloat(uc[1]) ];
                //console.log(bboxfloat);
                var ftLayer = { 
                    name: name,
                    title: title,
                    visible: false,
                    type: PublicaMundi.LayerType.WFS,
                    click: onFeatureClick,
                    bbox: bboxfloat,

                // layer: 'osm:water_areas&bbox=-190000,-190000,200000,200000,EPSG:3857',
                    url: url+ '?service=WFS&version=1.1.0&request=GetFeature&typename='+name+'&srsname=EPSG:4326&outputFormat=json'
                        //&maxFeatures=1000',
                };
            
                layerProcessor(ftLayer)
        

    
                    })
        
                                })
}

var parseWMSCapas = function(url, callback, failCallback) {
        
        $.ajax(url+"?request=GetCapabilities").then(function(response) {
            
            //console.log('response');
            //console.log(response);
            var capabilities = response.firstChild.getElementsByTagName("Layer");
            var bboxres = response.firstChild.getElementsByTagName("EX_GeographicBoundingBox")[0];
            
            var wblng = bboxres.getElementsByTagName('westBoundLongitude')[0].innerHTML;
            var eblng = bboxres.getElementsByTagName('eastBoundLongitude')[0].innerHTML;
            var sblat = bboxres.getElementsByTagName('southBoundLatitude')[0].innerHTML;
            var nblat = bboxres.getElementsByTagName('northBoundLatitude')[0].innerHTML;
            
            var bboxfloat = [ parseFloat(wblng), parseFloat(sblat), parseFloat(eblng), parseFloat(nblat) ];

            //console.log('capabilities');
            //console.log(capabilities);
            callback(capabilities, bboxfloat);

        });
    }

var withWMSLayers = function (resource, layerProcessor) {
    var parsedUrl = resource.url.split('#')
    var urlBody = parsedUrl[0].split('?')[0] // remove query if any
    var url = resource.proxy_service_url || urlBody

    var layerName = parsedUrl.length>1 && parsedUrl[1]

    parseWMSCapas(
        url,
        function(candidates, bbox) {
            if (layerName) candidates = candidates.filter(function(layer) {return layer.name == layerName})

            var ver = candidates.version
            $_.each(candidates, function(candidate, idx) {
                // TODO: Need to implement this in a better way
                var title = candidate.getElementsByTagName('Title')[0].innerHTML;
                var name = candidate.getElementsByTagName('Name')[0].innerHTML;

                var mapLayer = {
                    type: PublicaMundi.LayerType.WMS,
                    url: urlBody, // use the original URL for the getMap, as there's no need for a proxy for image request
                    transparent: true,
                    name: name,
                    title: title,
                    bbox: bbox,
                    visible: false,
                    params: {'LAYERS': name},
                };

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
    }

    var withArcGisLayers = function (resource, layerProcessor) {
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

    }


    var createArcgisFeatureLayer = function (url, descriptor, visible) {

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
    var info; 
    // TODO: handle click with overlay
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
            
            var layer = this.map.createLayer(resourceLayer);
        
        },

        _onReady: function () {

            var mapDiv = $("<div></div>").attr("id", "map-ol").addClass("map")
            info = $("<div></div>").attr("id", "info")
            info.css({
                    //left: pixel[0] + 'px',
                    //top: (pixel[1] - 15) + 'px'
                    left: '20px',
                    top: '50px'
                  });

            mapDiv.append(info)
            info.tooltip({
                  animation: true,
                  trigger: 'manual'
            });
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
            withLayers(preload_resource, $_.bind(this.addLayer, this))
        }
    }
});
