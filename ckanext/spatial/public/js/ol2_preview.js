// Openlayers preview module

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
                    this.ftDescr.bounds.transform(new OpenLayers.Projection("EPSG:4326"),this.map.getProjectionObject()))
                   || OpenLayers.Layer.Vector.prototype.getDataExtent.call(this, arguments)
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
                    inputId = OpenLayers.Util.createUniqueID(
                        this.id + "_input_"
                    );

                inputElem.id = inputId;
                inputElem.name = (baseLayer) ? this.id + "_baseLayers" : layer.name;
                inputElem.type = (baseLayer) ? "radio" : "checkbox";
                inputElem.value = layer.name;
                inputElem.checked = checked;
                inputElem.defaultChecked = checked;
                inputElem.className = "olButton";
                inputElem._layer = layer.id;
                inputElem._layerSwitcher = this.id;

                if (!baseLayer && !layer.inRange) {
                    inputElem.disabled = true;
                }

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
                // create line break
                var br = document.createElement("br");


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
                groupDiv.appendChild(br);
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
        wfsFormat = new OpenLayers.Format.WFSCapabilities();

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

    var createKMLLayer = function (resource) {
        var url = resource.proxy_url || resource.url

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

                var ftLayer = new OpenLayers.Layer.WFSLayer(ftName, {
                    ftDescr: candidate[0],
                    strategies: [new OpenLayers.Strategy.BBOXWithMax({maxFeatures: 300, ratio: 1})],
                    protocol: new OpenLayers.Protocol.WFS({
                        version: ver,
                        url: url,
                        featureType: candidate[0].name,
                        featureNS: undefined,
                        maxFeatures: 300
                    })
                })

                dfd.resolve(ftLayer)},
            function(args) {dfd.reject(args)})



        return dfd.promise()
    }

    var createGeoJSONLayer = function (resource) {
        var url = resource.proxy_url || resource.url

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
        'geojson': createGeoJSONLayer,
        'wfs': createFeatureTypeLayer
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

            var bbox = resourceLayer.getDataExtent && resourceLayer.getDataExtent()
            if (bbox) map.zoomToExtent(bbox)
            else {
                var firstExtent = false
                resourceLayer.events.register(
                    "loadend",
                    resourceLayer,
                    function(e) {
                        var bbox = e && e.object && e.object.getDataExtent && e.object.getDataExtent()
                        if (!firstExtent && bbox) {
                            map.zoomToExtent(bbox)
                            firstExtent = true
                        }
                        else map.zoomToMaxExtent()
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


