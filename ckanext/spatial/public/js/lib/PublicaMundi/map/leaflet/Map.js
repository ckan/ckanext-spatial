/// <reference path="../../../Leaflet/leaflet-src.js" />

/// <reference path="../../PublicaMundi.js" />
/// <reference path="../../PublicaMundi.Leaflet.js" />
/// <reference path="../Map.js" />

(function (window, PublicaMundi, L) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof L === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.Leaflet');

    PublicaMundi.Leaflet.Map = PublicaMundi.Class(PublicaMundi.Map, {
        initialize: function (options) {
            PublicaMundi.Map.prototype.initialize.call(this, options);

            this._unproject = function (location) {
                var projected = L.point(location[0], location[1]).divideBy(6378137);
                return L.CRS.EPSG3857.projection.unproject(projected);
            };

            if ((PublicaMundi.isClass('L.Map')) && (options instanceof L.Map)) {
                this._map = options;
            } else {
                // TODO : Resolve projection
                // implement min max zoom
                this._map = L.map(options.target, {
                    // TODO : Add projection
                    center: this._unproject(options.center),
                    zoom: options.zoom,
                    maxZoom: options.maxZoom,
                    minZoom: options.minZoom,
                    attributionControl: false
                });
            }

            if ((typeof options.layers !== 'undefined') && (PublicaMundi.isArray(options.layers))) {
                for (var index = 0; index < options.layers.length; index++) {
                    this.createLayer(options.layers[index]);

                }
            }
        },

        setLayerControl: function(base) {
            this._control = new L.control.layers();
            this._control.addTo(this._map);
            
            base.addToControl();
            return this._control;
        },
        setCenter: function (x, y) {
            if (PublicaMundi.isArray(x)) {
                this._map.setView(this._unproject(x), this._map.getZoom());
            } else {
                this._map.setView(this._unproject([x, y]), this._map.getZoom());
            }
        },
        getCenter: function () {
            var center = this._map.getCenter();
            center = L.CRS.EPSG3857.projection.project(center).multiplyBy(6378137);
            return [center.x, center.y];
        },
        setEvent: function (event, eventfunc) {
        //    this._map.on(event, eventfunc);
        },
        setExtent: function (extent){
            //this._map.on("layerAdd", this._map.setMaxBounds(new L.LatLngBounds(extent))); 
            this._map.fitBounds(extent);
        },
        setZoom: function (z) {
            this._map.setView(this._map.getCenter(), z);
        },
        getZoom: function () {
            return this._map.getZoom();
        },
        getProjection: function () {
            return 'EPSG:3857';
        },
        getTarget: function () {
            return this._map.getTarget();
        },
        addLayer: function (layer) {
            this._map.addLayer(layer.getLayer());
        }
    });

    PublicaMundi.locator.register('PublicaMundi.Map', PublicaMundi.Leaflet.Map);
})(window, window.PublicaMundi, L);
