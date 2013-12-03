// Openlayers preview module

var EPSG4326 = new OpenLayers.Projection("EPSG:4326")
var Mercator = new OpenLayers.Projection("EPSG:3857")
var CRS84 = new OpenLayers.Projection("urn:x-ogc:def:crs:EPSG:4326")

OpenLayers.Strategy.BBOXWithMax = OpenLayers.Class(OpenLayers.Strategy.BBOX, {
    update: function(options) {
        var mapBounds = this.getMapBounds();

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
                labelSpan.innerHTML = layer.name;
                labelSpan.style.verticalAlign = (baseLayer) ? "bottom"
                    : "baseline";


                var groupArray = (baseLayer) ? this.baseLayers
                    : this.dataLayers;
                groupArray.push({
                    'layer': layer,
                    'inputElem': inputElem,
                    'labelSpan': labelSpan
                });


                var groupDiv = (baseLayer) ? this.baseLayersDiv
                    : this.dataLayersDiv;
                groupDiv.appendChild(inputElem);
                groupDiv.appendChild(labelSpan);
            }

            // if no overlays, dont display the overlay label
            this.dataLbl.style.display = (containsOverlays) ? "" : "none";

            // if no baselayers, dont display the baselayer label
            this.baseLbl.style.display = (containsBaseLayers) ? "" : "none";

            return this.div;
        }
    }
)


this.ckan.module('olpreview', function (jQuery, _) {

    var proxy = false;

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


    var parseWFSFeatureTypeDescr = function(url, ftName, callback, failCallback) {
        var format = new OpenLayers.Format.WFSDescribeFeatureType()

        OpenLayers.Request.GET({
            url: url,
            params: {
                SERVICE: "WFS",
                REQUEST: "DescribeFeatureType",
                TYPENAME: ftName
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

    var createFeatureTypeLayer = function (resource) {
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var ftName = parsedUrl.length>1 && parsedUrl[1]

        var dfd = $.Deferred()

        parseWFSCapas(
            url,
            function(capas) {

                var candidate = capas.featureTypeList.featureTypes.filter(function(ft) {return ft.name == ftName})

                var ver = capas.version
                if (ver == "2.0.0") ver = "1.1.0"  // 2.0.0 causes failures in some cases (e.g. Geoserver TOPP States WFS)

                parseWFSFeatureTypeDescr(
                    url,
                    candidate[0].name,
                    function(descr) {

                        var geomProps = descr.featureTypes[0].properties.filter(function(prop) {return prop.type.startsWith("gml")})

                        var ftLayer = new OpenLayers.Layer.WFSLayer(ftName, {
                            ftDescr: candidate[0],
                            strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: 300, ratio: 1})],
                            projection: Mercator,
                            protocol: new OpenLayers.Protocol.WFS({
                                //headers:{"Accept-Charset":"utf-8"}, // (failed) attempt at dealing with accentuated chars in some feature types
                                version: ver,
                                url: url,
                                featureType: candidate[0].name,
                                srsName: Mercator,
                                featureNS: undefined,
                                maxFeatures: 300,
                                geometryName: (geomProps && geomProps.length>0)?geomProps[0].name:undefined
                            })
                        })

                        dfd.resolve(ftLayer)
                    },
                    function(args) {dfd.reject(args)})
            },
            function(args) {dfd.reject(args)})



        return dfd.promise()
    }


    var createWMSLayer = function (resource) {
        var parsedUrl = resource.url.split('#')
        var url = resource.proxy_service_url || parsedUrl[0]

        var layerName = parsedUrl.length>1 && parsedUrl[1]

        var dfd = $.Deferred()

        parseWMSCapas(
            url,
            function(capas) {

                var candidate = capas.capability.layers.filter(function(layer) {return layer.name == layerName})

                var ver = capas.version

                var mapLayer = new OpenLayers.Layer.WMSLayer(
                    layerName,
                    parsedUrl[0], // use the original URL for the getMap, as there's no need for a proxy for image requests
                    {layers: layerName,
                     transparent: true},
                    {mlDescr: candidate[0],
                     baseLayer: false,
                     singleTile: true,
                     projection: Mercator, // force SRS to 3857 if using OSM baselayer
                     ratio: 1
                    }
                )

                dfd.resolve(mapLayer)},
            function(args) {dfd.reject(args)})



        return dfd.promise()
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

    layerConstructors = {
        'kml': createKMLLayer,
        'gml': createGMLLayer,
        'geojson': createGeoJSONLayer,
        'wfs': createFeatureTypeLayer,
        'wms': createWMSLayer
    }

    var createLayer = function (resource) {
        var resourceUrl = resource.url
        var proxiedResourceUrl = resource.proxy_url
        var proxiedServiceUrl = resource.proxy_service_url

        var cons = layerConstructors[resource.format && resource.format.toLocaleLowerCase()]
        return cons && cons(resource)
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
            var basemapLayer = new OpenLayers.Layer.OSM( "Simple OSM Map")

            var mapDiv = $("<div></div>").attr("id", "map").addClass("map")
            var info = $("<div></div>").attr("id", "info")
            mapDiv.append(info)

            $("#data-preview").empty()
            $("#data-preview").append(mapDiv)

            info.tooltip({
                animation: false,
                trigger: 'manual',
                html: true
            });

            var map = new OpenLayers.Map(
                {
                    div: "map",
                    layers: [basemapLayer, resourceLayer],
                    maxExtent: basemapLayer.getMaxExtent(),
                    //projection: Mercator, // this is needed for WMS layers (most only accept 3857), but causes WFS to fail
                    eventListeners: {
                        featureover: function(e) {
                            e.feature.renderIntent = "select";
                            e.feature.layer.drawFeature(e.feature);
                            var pixel = event.xy
                            info.css({
                                left: pixel.x + 'px',
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

            map.addControl(new OpenLayers.Control.CKANLayerSwitcher());

            var bboxFrag
            var frags = ((window.parent || window).location.hash && (window.parent || window).location.hash.substring(1).split("&")) || []
            var fragMap = {}
            for (var idx in  frags) {
                var kv = frags[idx].split('=')
                fragMap[kv[0].toLowerCase()] = kv[1]
            }

            var bbox = (fragMap.bbox && new OpenLayers.Bounds(fragMap.bbox.split(',')).transform(EPSG4326,map.getProjectionObject())) ||
                       (resourceLayer.getDataExtent && resourceLayer.getDataExtent())
            if (bbox) map.zoomToExtent(bbox)
            else {
                var firstExtent = false
                resourceLayer.events.register(
                    "loadend",
                    resourceLayer,
                    function(e) {
                        if (!firstExtent) {
                            var bbox = e && e.object && e.object.getDataExtent && e.object.getDataExtent()
                            if (bbox)
                                map.zoomToExtent(bbox)
                            else
                                map.zoomToMaxExtent()
                            firstExtent = true
                        }
                    })
            }
        },

        _onReady: function () {
            var resourceLayer = createLayer(preload_resource)
            var $this = this;
            if (resourceLayer.done) resourceLayer.done(function(layer) {$this.addLayer(layer)})
            else this.addLayer(resourceLayer)


        }
    }
});


