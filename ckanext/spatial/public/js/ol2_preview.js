// Openlayers preview module

var $_ = _ // keep pointer to underscore, as '_' will be overridden by a closure variable when down the stack

var EPSG4326 = new OpenLayers.Projection("EPSG:4326")
var Mercator = new OpenLayers.Projection("EPSG:3857")
var CRS84 = new OpenLayers.Projection("urn:x-ogc:def:crs:EPSG:4326")

/*
var default_style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
default_style.fillOpacity = 0.2;
default_style.graphicOpacity = 1;
default_style.strokeWidth = "2";
*/


// override the XMLHttpRequest to enforce UTF-8 decoding
// because some WFS respond with UTF-8 answers while advertising ISO encoding in the headers
var originalXHR = OpenLayers.Request.XMLHttpRequest
OpenLayers.Request.XMLHttpRequest = function() {
    var newXHR = new originalXHR()
    if (newXHR._object && newXHR._object.overrideMimeType) newXHR._object.overrideMimeType('text/xml; charset=UTF-8')
    return newXHR
}
$_.each(Object.keys(originalXHR), function(key) {OpenLayers.Request.XMLHttpRequest[key] = originalXHR[key]})


OpenLayers.Strategy.BBOXWithMax = OpenLayers.Class(OpenLayers.Strategy.BBOX, {
    update: function(options) {
        var mapBounds = this.getMapBounds() || new OpenLayers.Bounds(-180, -90, 180, 90);

        var maxFeatures = this.layer.protocol && this.layer.protocol.maxFeatures

        if (mapBounds !== null && ((options && options.force) || ((this.layer.features && this.layer.features.length) >= maxFeatures) ||
            (this.layer.visibility && this.layer.calculateInRange() && this.invalidBounds(mapBounds)))) {
            this.calculateBounds(mapBounds);
            this.resolution = this.layer.map.getResolution();
            this.triggerRead(options);
        }
    }
})

OpenLayers.Layer.WFSLayer = OpenLayers.Class(OpenLayers.Layer.Vector,
    {
        getDataExtent: function () {
            return (this.ftDescr &&
                    this.ftDescr.bounds &&
                    this.ftDescr.bounds.transform(EPSG4326,this.map.getProjectionObject()))
                   || OpenLayers.Layer.Vector.prototype.getDataExtent.call(this, arguments)
        }
    }
)

OpenLayers.Layer.WMSLayer = OpenLayers.Class(OpenLayers.Layer.WMS,
    {
        getDataExtent: function () {
            return (this.mlDescr &&
                this.mlDescr.llbbox &&
                new OpenLayers.Bounds(this.mlDescr.llbbox).transform(EPSG4326,this.map.getProjectionObject()))
                || OpenLayers.Layer.WMS.prototype.getDataExtent.call(this, arguments)
        }
    }
)

OpenLayers.Control.CKANLayerSwitcher = OpenLayers.Class(OpenLayers.Control.LayerSwitcher,
    {
        redraw: function() {
            //if the state hasn't changed since last redraw, no need
            // to do anything. Just return the existing div.
            if (!this.checkRedraw()) {
                return this.div;
            }

            //clear out previous layers
            this.clearLayersArray("base");
            this.clearLayersArray("data");

            var containsOverlays = false;
            var containsBaseLayers = false;

            // Save state -- for checking layer if the map state changed.
            // We save this before redrawing, because in the process of redrawing
            // we will trigger more visibility changes, and we want to not redraw
            // and enter an infinite loop.
            this.layerStates = this.map.layers.map(function(layer) {
                return {
                    'name': layer.name,
                    'visibility': layer.visibility,
                    'inRange': layer.inRange,
                    'id': layer.id
                };
            })

            var layers = this.map.layers.slice().filter(function(layer) {return layer.displayInLayerSwitcher});
            if (!this.ascending) { layers.reverse(); }

            for(var i=0; i<layers.length; i++) {
                var layer = layers[i];
                var baseLayer = layer.isBaseLayer;

                if (baseLayer) containsBaseLayers = true;
                else containsOverlays = true;

                // only check a baselayer if it is *the* baselayer, check data
                //  layers if they are visible
                var checked = (baseLayer) ? (layer == this.map.baseLayer) : layer.getVisibility();

                // create input element
                var inputElem = document.createElement("input"),
                    // The input shall have an id attribute so we can use
                    // labels to interact with them.
                    inputId = OpenLayers.Util.createUniqueID(this.id + "_input_");

                inputElem.id = inputId;
                inputElem.name = (baseLayer) ? this.id + "_baseLayers" : layer.name;
                inputElem.type = (baseLayer) ? "radio" : "checkbox";
                inputElem.value = layer.name;
                inputElem.checked = checked;
                inputElem.defaultChecked = checked;
                inputElem.className = "olButton";
                inputElem._layer = layer.id;
                inputElem._layerSwitcher = this.id;
                inputElem.disabled = !baseLayer && !layer.inRange;

                // create span
                var labelSpan = document.createElement("label");
                // this isn't the DOM attribute 'for', but an arbitrary name we
                // use to find the appropriate input element in <onButtonClick>
                labelSpan["for"] = inputElem.id;
                OpenLayers.Element.addClass(labelSpan, "labelSpan olButton");
                labelSpan._layer = layer.id;
                labelSpan._layerSwitcher = this.id;
                if (!baseLayer && !layer.inRange) {
                    labelSpan.style.color = "gray";
                }
                labelSpan.innerHTML = layer.title || layer.name;
                labelSpan.style.verticalAlign = (baseLayer) ? "bottom"
                    : "baseline";


                var groupArray = (baseLayer) ? this.baseLayers
                    : this.dataLayers;
                groupArray.push({
                    'layer': layer,
                    'inputElem': inputElem,
                    'labelSpan': labelSpan
                });


                var groupDiv = $((baseLayer) ? this.baseLayersDiv
                    : this.dataLayersDiv);
                groupDiv.append($("<div></div>").append($(inputElem)).append($(labelSpan)));
            }

            // if no overlays, dont display the overlay label
            this.dataLbl.style.display = (containsOverlays) ? "" : "none";

            // if no baselayers, dont display the baselayer label
            this.baseLbl.style.display = (containsBaseLayers) ? "" : "none";

            return this.div;
        }
    }
)

/**
 * Parse a comma-separated set of KVP, typically for URL query or fragments
 * @param url
 */
var parseKVP = function(kvpString) {
    var kvps = (kvpString && kvpString.split("&")) || []
    var kvpMap = {}
    for (var idx in  kvps) {
        var kv = kvps[idx].split('=')
        kvpMap[kv[0].toLowerCase()] = kv[1]
    }

    return kvpMap
}

/**
 * Parse a comma-separated set of KVP, typically for URL query or fragments
 * @param url
 */
var parseURL = function(url) {
    var parts = url.split('?',2)
    var path = parts[0]
    var query = parts.length>1 && parts[1]
    var hash
    if (!query) {
        parts = path.split('#', 2)
        path = parts[0]
        hash = parts.length>1 && parts[1]
    } else {
        parts = query.split('#', 2)
        query = parts[0]
        hash = parts.length>1 && parts[1]
    }

    return {
        path: path,
        query: parseKVP(query),
        hash: parseKVP(hash)
    }
}


this.ckan.module('olpreview', function (jQuery, _) {

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
        var wfsFormat = new OpenLayers.Format.WFSCapabilities();

        OpenLayers.Request.GET({
            url: url,
            params: {
                SERVICE: "WFS",
                REQUEST: "GetCapabilities"
            },
            success: function(request) {
                var doc = request.responseXML;
                if (!doc || !doc.documentElement) {
                    doc = request.responseText;
                }
                var capabilities = wfsFormat.read(doc)
                callback(capabilities)
            },
            failure: failCallback || function() {
                alert("Trouble getting capabilities doc");
                OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
            }
        });
    }


    var parseWFSFeatureTypeDescr = function(url, ftName, ver, callback, failCallback) {
        var format = new OpenLayers.Format.WFSDescribeFeatureType()

        OpenLayers.Request.GET({
            url: url,
            params: {
                SERVICE: "WFS",
                REQUEST: "DescribeFeatureType",
                TYPENAME: ftName,
                VERSION: ver
            },
            success: function(request) {
                var doc = request.responseXML;
                if (!doc || !doc.documentElement) {
                    doc = request.responseText;
                }
                var descr = format.read(doc)
                callback(descr)
            },
            failure: failCallback || function() {
                alert("Trouble getting ft decription doc");
                OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
            }
        });
    }

    var parseWMSCapas = function(url, callback, failCallback) {
        var wmsFormat = new OpenLayers.Format.WMSCapabilities();

        OpenLayers.Request.GET({
            url: url,
            params: {
                SERVICE: "WMS",
                REQUEST: "GetCapabilities"
            },
            success: function(request) {
                var doc = request.responseXML;
                if (!doc || !doc.documentElement) {
                    doc = request.responseText;
                }
                var capabilities = wmsFormat.read(doc)
                callback(capabilities)
            },
            failure: failCallback || function() {
                alert("Trouble getting capabilities doc");
                OpenLayers.Console.error.apply(OpenLayers.Console, arguments);
            }
        });
    }

    var createKMLLayer = function (resource) {
        var url = resource.proxy_url || resource.url

        var kml = new OpenLayers.Layer.Vector("KML", {
            projection: EPSG4326,
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
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

        parseWFSCapas(
            url,
            function(capas) {

                var ver = capas.version
                if (ver == "2.0.0") ver = "1.1.0"  // 2.0.0 causes failures in some cases (e.g. Geoserver TOPP States WFS)

                var candidates = capas.featureTypeList.featureTypes
                if (ftName) candidates = candidates.filter(function(ft) {return ft.name == ftName})

                $_.each(candidates, function(candidate, idx) {
                    parseWFSFeatureTypeDescr(
                        url,
                        candidate.name,
                        ver,
                        function(descr) {
                            if (descr.featureTypes) {
                                var geomProps = descr.featureTypes[0].properties.filter(function(prop) {return prop.type.startsWith("gml")})

                                // ignore feature types with no gml prop. Correct ?
                                if (geomProps && geomProps.length > 0) {

                                    var ftLayer = new OpenLayers.Layer.WFSLayer(
                                        candidate.name, {
                                        //style: default_style,
                                        ftDescr: candidate,
                                        title: candidate.title,
                                        strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: 300, ratio: 1})],
                                        projection: Mercator,
                                        visibility: idx==0,
                                        protocol: new OpenLayers.Protocol.WFS({
                                            headers:{"Content-Type":"application/xml; charset=UTF-8"}, // (failed) attempt at dealing with accentuated chars in some feature types
                                            version: ver,
                                            url: url,
                                            featureType: candidate.name,
                                            srsName: Mercator,
                                            featureNS: undefined,
                                            maxFeatures: 300,
                                            geometryName: geomProps[0].name
                                        })
                                    })

                                    layerProcessor(ftLayer)
                                }
                            }
                        }
                    )
                })

            }
        )
    }


    var withWMSLayers = function (resource, layerProcessor) {
        var parsedUrl = resource.url.split('#')
        var urlBody = parsedUrl[0].split('?')[0] // remove query if any
        var url = resource.proxy_service_url || urlBody

        var layerName = parsedUrl.length>1 && parsedUrl[1]

        parseWMSCapas(
            url,
            function(capas) {

                var candidates = capas.capability.layers
                if (layerName) candidates = candidates.filter(function(layer) {return layer.name == layerName})

                var ver = capas.version

                $_.each(candidates, function(candidate, idx) {
                    var mapLayer = new OpenLayers.Layer.WMSLayer(
                        candidate.name,
                        urlBody, // use the original URL for the getMap, as there's no need for a proxy for image requests
                        {layers: candidate.name,
                            transparent: true},
                        {mlDescr: candidate,
                            title: candidate.title,
                            baseLayer: false,
                            singleTile: true,
                            visibility: idx==0,
                            projection: Mercator, // force SRS to 3857 if using OSM baselayer
                            ratio: 1
                        }
                    )

                    layerProcessor(mapLayer)
                })

                }
            )

    }

    var createGeoJSONLayer = function (resource) {
        var url = resource.proxy_url || resource.url

        var geojson = new OpenLayers.Layer.Vector(
            "GeoJSON",
            {
                projection: EPSG4326,
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: url,
                    format: new OpenLayers.Format.GeoJSON()
            })
        });

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
                strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: 300, ratio: 1})],
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

    /*
    var createLayers = function (resource) {
        var resourceUrl = resource.url
        var proxiedResourceUrl = resource.proxy_url
        var proxiedServiceUrl = resource.proxy_service_url

        var cons = layerExtractors[resource.format && resource.format.toLocaleLowerCase()]
        return cons && cons(resource)
    }
    */

    var withLayers = function(resource, layerProcessor) {
        var resourceUrl = resource.url
        var proxiedResourceUrl = resource.proxy_url
        var proxiedServiceUrl = resource.proxy_service_url

        var withLayers = layerExtractors[resource.format && resource.format.toLocaleLowerCase()]
        withLayers && withLayers(resource, layerProcessor)
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

        addLayer: function(resourceLayer) {
            this.map.addLayer(resourceLayer)

            var bbox = resourceLayer.getDataExtent && resourceLayer.getDataExtent()
            if (bbox) {
                if (this.map.getExtent()) this.map.getExtent().extend(bbox)
                else this.map.zoomToExtent(bbox)
            }
            else {
                var firstExtent = false
                resourceLayer.events.register(
                    "loadend",
                    resourceLayer,
                    function(e) {
                        if (!firstExtent) {
                            var bbox = e && e.object && e.object.getDataExtent && e.object.getDataExtent()
                            if (bbox)
                                if (this.map.getExtent()) this.map.getExtent().extend(bbox)
                                else this.map.zoomToExtent(bbox)
                            else
                                this.map.zoomToMaxExtent()
                            firstExtent = true
                        }
                    })
            }

        },

        _onReady: function () {
            var basemapLayer = new OpenLayers.Layer.OSM( "Simple OSM Map")

            var mapDiv = $("<div></div>").attr("id", "map").addClass("map")
            var info = $("<div></div>").attr("id", "info")
            mapDiv.append(info)

            $("#data-preview").empty()
            $("#data-preview").append(mapDiv)

            info.tooltip({
                animation: false,
                trigger: 'manual',
                placement: "right",
                html: true
            });

            this.map = new OpenLayers.Map(
                {
                    div: "map",
                    layers: [basemapLayer],
                    maxExtent: basemapLayer.getMaxExtent(),
                    //projection: Mercator, // this is needed for WMS layers (most only accept 3857), but causes WFS to fail
                    eventListeners: {
                        featureover: function(e) {
                            e.feature.renderIntent = "select";
                            e.feature.layer.drawFeature(e.feature);
                            var pixel = event.xy
                            info.css({
                                left: (pixel.x + 10) + 'px',
                                top: (pixel.y - 15) + 'px'
                            });
                            info.currentFeature = e.feature
                            info.tooltip('hide')
                                .empty()
                            var tooltip = "<div>"+(e.feature.data.name || e.feature.fid)+"</div><table>";
                            for (var prop in e.feature.data) tooltip += "<tr><td>"+prop+"</td><td>"+ e.feature.data[prop]+"</td></tr></div>"
                            tooltip += "</table>"
                            info.attr('data-original-title', tooltip)
                                .tooltip('fixTitle')
                                .tooltip('show');
                        },
                        featureout: function(e) {
                            e.feature.renderIntent = "default"
                            e.feature.layer.drawFeature(e.feature)
                            if (info.currentFeature == e.feature) {
                                info.tooltip('hide')
                                info.currentFeature = undefined
                            }

                        },
                        featureclick: function(e) {
                            //log("Map says: " + e.feature.id + " clicked on " + e.feature.layer.name);
                        }
                    }
                });

            this.map.addControl(new OpenLayers.Control.CKANLayerSwitcher());

            var bboxFrag
            var fragMap = parseKVP((window.parent || window).location.hash && (window.parent || window).location.hash.substring(1))

            var bbox = (fragMap.bbox && new OpenLayers.Bounds(fragMap.bbox.split(',')).transform(EPSG4326,this.map.getProjectionObject()))
            if (bbox) this.map.zoomToExtent(bbox)

            withLayers(preload_resource, $_.bind(this.addLayer, this))

            /*
            var resourceLayers = createLayers(preload_resource)
            var $this = this;

            if (! (resourceLayers instanceof Array)) resourceLayers = [resourceLayers]
            $_.each(resourceLayers, function(resourceLayer) {
                if (resourceLayer.done) resourceLayer.done(function(layer) {$this.addLayer(layer)})
                else $this.addLayer(resourceLayer)
            })
            */



        }
    }
});


