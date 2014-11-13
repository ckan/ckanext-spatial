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
        
        $.ajax(url+"?service=WFS&request=GetCapabilities").then(function(response) {
            
            //console.log('wfs capas');
            //var capabilities = response.firstChild.getElementsByTagName("FeatureType");
            //if (capabilities == null){
            //    capabilities = response.firstChild.getElementsByTagName("wfs:FeatureType");
            //}
            //var response = parser.read(response);
            response = xmlToJson(response);
            //console.log(response);
            //console.log(response_json);
            var capabilities = response["wfs:WFS_Capabilities"]["FeatureTypeList"];
            //console.log(capabilities);
            if (typeof capabilities === "undefined") {
                capabilities = response["wfs:WFS_Capabilities"]["wfs:FeatureTypeList"]["wfs:FeatureType"];
            }
            else{ 
                capabilities = capabilities["FeatureType"];
            }
            
            //console.log(capabilities);
            //json = xmlToJson(candidate);
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
                    //console.log('wfs item');
                    //console.log(candidate);

                    //json = xmlToJson(candidate);
                    //console.log(json);
                    var title = candidate["Title"];
                    if (typeof title === "undefined") {
                        title = candidate["wfs:Title"];
                    }
                    title = title["#text"];
                    //console.log(title);
                    
                    var name = candidate["Name"];
                    if (typeof name === "undefined") {
                        name = candidate["wfs:Name"];
                    }
                    name = name["#text"];
                    //console.log(name);
                    
                    var bbox = candidate["WGS84BoundingBox"];
                    var lc = null;
                    var uc = null;
                    if (typeof bbox === "undefined") {
                        bbox = candidate["ows:WGS84BoundingBox"];
                        lc = bbox['ows:LowerCorner']["#text"];
                        uc = bbox['ows:UpperCorner']["#text"];
                    }
                    else {
                        lc = bbox['LowerCorner']["#text"];
                        uc = bbox['UpperCorner']["#text"];
                    }
                    //console.log(bbox);
                    
                    //[0].innerHTML;
                        //[0].innerHTML;
                     //   console.log(lc);
                     //   console.log(uc);

                        lc = lc.split(' ');
                        uc = uc.split(' ');
                        bboxfloat = [ parseFloat(lc[0]), parseFloat(lc[1]), parseFloat(uc[0]), parseFloat(uc[1]) ];
                    
                        //var title = candidate.getElementsByTagName('Title')[0].innerHTML;
                    //console.log('in wfs');
                    //console.log('xml');
                    //console.log(candidate);
                    //dom = parseXml(candidate);
                    //json = xmlToJson(candidate);
                    //console.log('json');
                    //console.log(json);
                    //["ows:LowerCorner"]["#text"]);
                    //var name = candidate.getElementsByTagName('Name')[0].innerHTML;
                    //var bbox = candidate.getElementsByTagName('WGS84BoundingBox');
                    //if (bbox.length==0) {
                    //    bbox = candidate.getElementsByTagName('ows:WGS84BoundingBox');
                if (bboxfloat) {
                    var ftLayer = { 
                        name: name,
                        title: title,
                        visible: false,
                        type: PublicaMundi.LayerType.WFS,
                        click: onFeatureClick,
                        bbox: bboxfloat,

                        url: url+ '?service=WFS&version=1.1.0&request=GetFeature&typename='+name+'&srsname=EPSG:4326&outputFormat=json'
                            //&maxFeatures=10'
                            //&maxFeatures=1000',
                    };
                    }
                else {
                    var ftLayer = { 
                        name: name,
                        title: title,
                        visible: false,
                        type: PublicaMundi.LayerType.WFS,
                        click: onFeatureClick,
                        url: url+ '?service=WFS&version=1.1.0&request=GetFeature&typename='+name+'&srsname=EPSG:4326&outputFormat=json'
                    };
                }

            
                layerProcessor(ftLayer)
        
                    })
        
                                })
}

var parseWMSCapas = function(url, callback, failCallback) {
       
        var parser = new ol.format.WMSCapabilities();
        $.ajax(url+"?service=WMS&request=GetCapabilities").then(function(response) {
            var response = parser.read(response);
            //console.log(response);
            var capabilities = response["Capability"]["Layer"]["Layer"];
            //console.log(capabilities);

            callback(capabilities);

        });
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
            //console.log('candidates');
            //if (!(candidates instanceof Array)){
            //    console.log('not array');
            //    candidates = [ candidates ];
            //}
            //
            //if (candidates["Layer"]) {
            //    console.log('has layer field');
            //    if (candidates["Layer"] instanceof Array){
            //        candidates = candidates ["Layer"];
            //    }
            //    else {
            //        candidates = [ candidates ["Layer"] ];
            //    }
            //}
            //console.log(candidates);
            //var ver = candidates.version
            $_.each(candidates, function(candidate, idx) {
                // TODO: Need to implement this in a better way
                //var title = candidate.getElementsByTagName('Title')[0].innerHTML;
                //var name = candidate.getElementsByTagName('Name')[0].innerHTML;
                //console.log('candidate');
                //console.log(candidate);
                var title = candidate["Title"];
                var name = candidate["Name"];
                var bbox = candidate["BoundingBox"];
                var bboxfloat=null;
                    $_.each(bbox, function(entry, idx) {
                        //console.log('entry=');
                        //console.log(entry);
                            var at = entry;
                            if (extractBbox(at) != null) {
                                bboxfloat = extractBbox(at);
                            }
                            });
                if (bboxfloat){
                    var mapLayer = {
                        type: PublicaMundi.LayerType.WMS,
                        url: urlBody, // use the original URL for the getMap, as there's no need for a proxy for image request
                        transparent: true,
                        name: name,
                        title: title,
                        bbox: bboxfloat,
                        visible: false,
                        params: {'LAYERS': name},
                    };

                }
                else{
                    var mapLayer = {
                        type: PublicaMundi.LayerType.WMS,
                        url: urlBody, // use the original URL for the getMap, as there's no need for a proxy for image request
                        transparent: true,
                        name: name,
                        title: title,
                        visible: false,
                        params: {'LAYERS': name},
                    };

                }
                //console.log('mapLayer');
                //console.log(mapLayer);
                
                layerProcessor(mapLayer)
                })

                }
            )

    }
    
    var extractBbox = function (at) {
        if (at["crs"] == "CRS:84") {
            bboxfloat = [ at["extent"][0], at["extent"][1], at["extent"][2], at["extent"][3] ];
            return bboxfloat;
        }
        else if(at["crs"] == "EPSG:4326") {
            bboxfloat = [ at["extent"][1], at["extent"][0], at["extent"][3], at["extent"][2] ];
            return bboxfloat;
        }
        else {
            return null;
        }
    }
    var createGeoJSONLayer = function (resource) {
        
        var url = resource.proxy_url || resource.url
        
            var geojson = {
                title: 'GeoJson',
               // projection: ol.proj.get("EPSG:3857"), 
                type: PublicaMundi.LayerType.GeoJSON,
                url: url,
                visible: false,
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
    var popup;
    // TODO: handle click with overlay
    var onFeatureClick = function (features, pixel) {
            //console.log('feature');
            if (features) {
                feature = features [0];
            }

            var element = popup.getElement();
            //var element = popup;
              var coordinate = pixel;

                $(document.getElementById('popup')).popover('destroy');
                  popup.setPosition(coordinate);
                  //popup.setLatLng([0, 0]);
                    // the keys are quoted to prevent renaming in ADVANCED_OPTIMIZATIONS mode.
                    var text;
                    if (feature['name']) { 
                        text =feature['name'];
                    }
                    else {
                        text = JSON.stringify(feature);
                    }
                       $(element).popover({
                            'placement': 'top',
                            'animation': false,
                            'html': true,
                            'content': text
                        }).attr('data-original-title');

                    $(element).popover('show');

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
            // set map extent on layer bounds
            layer.setLayerExtent();
        
        },

        _onReady: function () {

            var mapDiv = $("<div></div>").attr("id", "map-ol").addClass("map")
            info = $("<div></div>").attr("id", "info")
            popup = $("<div></div>").attr("id", "popup")
            
            mapDiv.append(info)
            mapDiv.append(popup)
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
                center: [-985774, 4016449],
                zoom: 1.6,
                layers: baseLayers,
                minZoom: 1,
                maxZoom: 18,
            };
            this.map = PublicaMundi.map(options);

            // Popup showing the position the user clicked
            // Need to make this by using the API
            //popup = this.map.addOverlay(document.getElementById('popup'))

            popup = new ol.Overlay({
               element: document.getElementById('popup')
               });
               this.map._map.addOverlay(popup);
                
               $(document.getElementById('map-ol')).click(function() {
                    $(document.getElementById('popup')).popover('destroy');
            });
            //console.log('map');
            //console.log(this.map);
            withLayers(preload_resource, $_.bind(this.addLayer, this))
        }
    }
});
