(function (window, PublicaMundi) {
    "use strict";

    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    PublicaMundi.Map = PublicaMundi.Class({
        initialize: function (options) {
            this._map = null;
            this._layers = [];
            this._control = null;
            this._viewbox = '0,0,0,0';

            options = options || {};
            options.target = (PublicaMundi.isDefined(options.target) ? options.target : null);
            options.projection = (PublicaMundi.isDefined(options.projection) ? options.projection : 'EPSG:3857');
            options.center = (PublicaMundi.isDefined(options.center) ? options.center : [0, 0]);
            options.zoom = (PublicaMundi.isDefined(options.zoom) ? options.zoom : 2);

        },
        setExtent: function(extent) {
            return this;
        },
        setViewBox: function() {
            return this;
        },
        getViewBox: function() { 
            return this._viewbox;
        },
        setLayerControl: function(c) {
            return this;
        },
        getLayerControl: function() {
            return this._control;
        },
        getMap: function () {
            return this._map;
        },
        setCenter: function (x, y) {
            return this;
        },
        getCenter: function () {
            return null;
        },
        setZoom: function (z) {
            return this;
        },
        getZoom: function () {
            return null;
        },
        getProjection: function () {
            return null;
        },
        getTarget: function () {
            return null;
        },
        getLayers: function() {
            return this._layers;
        },
        listen: function() { 
            return null;
        },

        createLayer: function (options) {
            var layer = null;

            switch (typeof options) {
                case 'string':
                    // Try to guess the data type
                    var suffixes = ['.gson', '.geojson'];
                    if (suffixes.some(function (item) { return options.indexOf(item, options.length - item.length); })) {
                        this.createLayer({
                            type: PublicaMundi.LayerType.GeoJSON,
                            url: options,
                            projection : this.getProjection()
                        });
                    }
                    break;
                case 'object':
                    var factories = PublicaMundi.registry.getFactories();
                    for (var r = 0; r < factories.length; r++) {
                        if (options instanceof factories[r]) {
                            layer = options;
                            break;
                        }
                    }
                    if (!layer) {
                        if (!PublicaMundi.isDefined(options.projection)) {
                            options.projection = this.getProjection();
                        }
                        layer = PublicaMundi.registry.createLayer(options);
                        layer.setMap(this);
                    }
                    if (layer) {
                        this.addLayer(layer);
                    } else {
                        console.log('Layer of type ' + options.type + ' is not supported.');
                    }
                    break;
            }

            if (layer) {
                this._layers.push(layer);
            }

            return layer;
        },
        addLayer: function (layer) {
        }
    });

    // Register new types to service locator
    PublicaMundi.locator.register('PublicaMundi.Map', PublicaMundi.Map);

    // Create factory method
    PublicaMundi.map = function (options) {
        return PublicaMundi.locator.create('PublicaMundi.Map', options);
    };

    // Initialize a map by a single url (see examples)
    PublicaMundi.configure = function (target, url, onLoad) {
        var _map = (typeof target === 'string' ? PublicaMundi.map({ target: target }) : PublicaMundi.map(target));

        jQuery.getJSON(url, function (data) {
            if (data.center) {
                _map.setCenter(data.center);
            }
            if (data.zoom) {
                _map.setZoom(data.zoom);
            }
            if (PublicaMundi.isArray(data.layers)) {
                for (var l = 0; l < data.layers.length; l++) {
                    _map.addLayer(data.layers[l]);
                }
            }
            if (PublicaMundi.isFunction(onLoad)) {
                onLoad.call(this, data);
            }
        });

        return _map;
    };

})(window, window.PublicaMundi);
