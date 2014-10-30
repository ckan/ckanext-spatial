(function (window, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers');

    PublicaMundi.OpenLayers.Map = PublicaMundi.Class(PublicaMundi.Map, {
        // TODO: not functional
        uncheckLayers: function() {
            $('.layer-switcher .panel ul').children().each(function () { console.log($(this).find('input')); $(this).find('input').attr('checked', false);}); // Unchecks it
        },
        setExtent: function(extent) {
                var transformation = ol.proj.transform(extent, 'EPSG:4326', 'EPSG:3857');
                this._map.getView().fitExtent(transformation, this._map.getSize());
        },

        initialize: function (options) {
            PublicaMundi.Map.prototype.initialize.call(this, options);

            if ((PublicaMundi.isClass('ol.Map')) && (options instanceof ol.Map)) {
                this._map = options;
            } else {
                this._map = new ol.Map({
                    target: options.target,
                    view: new ol.View2D({
                        projection: options.projection,
                        center: options.center,
                        zoom: options.zoom
                    }),
                    controls: ol.control.defaults().extend([
                    ]),
                    ol3Logo: false
                });
            }
            
            this.listen();
            this._clickHandlerMap = null;
            this._clickHandlerLayer = [];
            this._clickHandlerRegisteredLayers = [];

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
                                handlers[l](features);
                            }
                        }
                    };

                    // Register only once
                    this._map.on('singleclick', this._clickHandlerMap, this);
                }
            }
            // set map extent to layer extent if present
            if (layer.getOptions().bbox) {
                this.setExtent(layer.getOptions().bbox);
            }

        },
        setLayerControl: function(control) {
            this._control = new ol.control.LayerSwitcher();
            this._map.getControls().extend([this._control]);

            return this._control;
        },
        setViewBox: function() {
            var bbox = this.getExtent()[0] + ',' + this.getExtent()[1] +',' + this.getExtent()[2] +','+ this.getExtent()[3];
            this._viewbox = bbox; 
        },

        getExtent: function() {
            return this._map.getView().getView2D().calculateExtent(this._map.getSize());
        },
        listen: function() {
            var map = this;
            var idx = 0;

            this.setLayerControl(this._map.getLayers()[0]);
            this._map.getLayers().on('add', function() {
             });

            this._map.on('moveend', function() {
                map.setViewBox();
            });

        },

    });


    PublicaMundi.locator.register('PublicaMundi.Map', PublicaMundi.OpenLayers.Map);
})(window, window.PublicaMundi, ol);
