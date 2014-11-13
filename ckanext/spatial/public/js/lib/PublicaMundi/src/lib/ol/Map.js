(function (window, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers');

    PublicaMundi.OpenLayers.Map = PublicaMundi.Class(PublicaMundi.Map, {
        addOverlay: function(element) {
            popup = new ol.Overlay({
                element: element
            });
            this._map.addOverlay(popup);
            return popup;
        },
        setExtent: function(extent, proj) {
            if (extent == null) {
                return;
            }
            var transformation;    
            if (proj == 'EPSG:4326') {
                    if (extent[0]< -180.0) {
                        extent[0] = -179.0;
                    }
                    if (extent[1] < -90.0) {
                        extent[1] = -89.0;
                    }
                    if (extent[2] > 180.0) {
                        extent[2] = 179.0;
                    }
                    if (extent[3] > 90.0) {
                        extent[3] = 89.0;
                    }
                    //console.log(extent);
                    transformation = ol.proj.transform(extent, 'EPSG:4326', 'EPSG:3857');
            }
            else if (proj == 'EPSG:3857'){
                transformation = extent;
            }
            else {
                transformation = null;
            }
                //console.log('showing extent');
                //console.log(transformation);
                this._map.getView().fitExtent(transformation, this._map.getSize());
        },
        initialize: function (options) {
            PublicaMundi.Map.prototype.initialize.call(this, options);

            if ((PublicaMundi.isClass('ol.Map')) && (options instanceof ol.Map)) {
                this._map = options;
            } else {
                this._map = new ol.Map({
                    target: options.target,
                    //view: new ol.View2D({
                    view: new ol.View({
                        projection: options.projection,
                        center: options.center,
                        zoom: options.zoom,
                        maxZoom: options.maxZoom,
                        minZoom: options.minZoom
                    }),
                    controls: ol.control.defaults().extend([
                    ]),
                    ol3Logo: false
                });
            }
            
            this._listen();
            this._clickHandlerMap = null;
            this._clickHandlerLayer = [];
            this._clickHandlerRegisteredLayers = [];
            
            this._map.on('click', function(e) {
                //console.log(e.coordinate);
                //transformation = ol.proj.transform(e.coordinate, 'EPSG:3857', 'EPSG:4326');
                //console.log(transformation);
            });
            if ((typeof options.layers !== 'undefined') && (PublicaMundi.isArray(options.layers))) {
                for (var index = 0; index < options.layers.length; index++) {
                    this.createLayer(options.layers[index]);

                }
            }
        },
        setCenter: function (x, y) {
            if (PublicaMundi.isArray(x)) {
                this._map.getView().setCenter(x);
            } else {
                this._map.getView().setCenter([x, y]);
            }
        },
        getCenter: function () {
            return this._map.getView().getCenter();
        },
        setZoom: function (z) {
            this._map.getView().setZoom(z);
        },
        getZoom: function () {
            return this._map.getView().getZoom();
        },
        getProjection: function () {
            return this._map.getView().getProjection().getCode();
        },
        getTarget: function () {
            return this._map.getTarget();
        },
        addLayer: function (layer) {
            this._map.addLayer(layer.getLayer());
            if (PublicaMundi.isFunction(layer.getOptions().click)) {
                this._clickHandlerRegisteredLayers.push(layer);
                this._clickHandlerLayer.push(layer.getOptions().click);

                if (!PublicaMundi.isFunction(this._clickHandlerMap)) {
                    var layers = this._clickHandlerRegisteredLayers;
                    var handlers = this._clickHandlerLayer;

                    this._clickHandlerMap = function (e) {
                        var pixel = this._map.getEventPixel(e.originalEvent);
                        var features = [];

                        var processFeature = function (feature, layer) {
                            if ((layer === layers[l].getLayer()) && (layer.get("visible") === true)) {
                                var properties = {};
                                var keys = feature.getKeys();
                                var geometryName = feature.getGeometryName();
                                for (var i = 0; i < keys.length; i++) {
                                    if (keys[i] !== geometryName) {
                                        properties[keys[i]] = feature.get(keys[i]);
                                    }
                                }
                                features.push(properties);
                            }
                        };

                        for (var l = 0; l < layers.length; l++) {
                            features = [];

                            this._map.forEachFeatureAtPixel(pixel, processFeature);

                            if (features.length > 0) {
                                //handlers[l](features, pixel);
                                
                                handlers[l](features, e.coordinate);
                            }
                        }
                    };

                    // Register only once
                    this._map.on('singleclick', this._clickHandlerMap, this);
                }
            }
            

        },
        _setLayerControl: function(control) {
            this._control = new ol.control.LayerSwitcher();
            this._map.getControls().extend([this._control]);

            return this._control;
        },
        _setViewBox: function() {
            var bbox = this.getExtent()[0] + ',' + this.getExtent()[1] +',' + this.getExtent()[2] +','+ this.getExtent()[3];
            this._viewbox = bbox; 
        },
        getExtent: function() {
            return this._map.getView().calculateExtent(this._map.getSize());
        },
        _listen: function() {
            var map = this;
            var idx = 0;
            //console.log('listening');
            this._setLayerControl(this._map.getLayers()[0]);
            //this._map.on('layeradd', function() {
            //    console.log('layer added');
            //    this._setLayerExtent();
            //});

            this._map.on('moveend', function() {
                map._setViewBox();
            });

        },

    });


    PublicaMundi.locator.register('PublicaMundi.Map', PublicaMundi.OpenLayers.Map);
})(window, window.PublicaMundi, ol);
