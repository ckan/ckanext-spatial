// Dataset map module
this.ckan.module('dataset-map', function (jQuery, _) {

  return {
    options: {
      i18n: {
      },
      styles: {
        point:{
          iconUrl: '/img/marker.png',
          iconSize: [14, 25],
          iconAnchor: [7, 25]
        },
        default_:{
          color: '#B52',
          weight: 2,
          opacity: 1,
          fillColor: '#FCF6CF',
          fillOpacity: 0.4
        }
      }
    },

    initialize: function () {

      this.extent = this.el.data('extent');

      // fix bbox when w-long is positive while e-long is negative.
      if (this.extent.type == 'Polygon'
        && this.extent.coordinates[0].length == 5) {
        _coordinates = this.extent.coordinates
        s = _coordinates[0][0][1];
        w = _coordinates[0][0][0];
        n = _coordinates[0][2][1];
        e = _coordinates[0][1][0];
        while (w > e) w -=360

        this.extent.coordinates = [[[w,s],[e,s],[e,n],[w,n],[w,s]]]
      };

      // hack to make leaflet use a particular location to look for images
      L.Icon.Default.imagePath = this.options.site_url + 'js/vendor/leaflet/images';

      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);

    },

    _onReady: function(){

      var map, backgroundLayer, extentLayer, ckanIcon;

      if (!this.extent) {
          return false;
      }

      map = ckan.commonLeafletMap('dataset-map-container', this.options.map_config, {attributionControl: false});

      var ckanIcon = L.Icon.extend({options: this.options.styles.point});

      var extentLayer = L.geoJson(this.extent, {
          style: this.options.styles.default_,
          pointToLayer: function (feature, latLng) {
            return new L.Marker(latLng, {icon: new ckanIcon})
          }});
      extentLayer.addTo(map);

      if (this.extent.type == 'Point'){
        map.setView(L.latLng(this.extent.coordinates[1], this.extent.coordinates[0]), 9);
      } else {
        map.fitBounds(extentLayer.getBounds());
      }
    }
  }
});
