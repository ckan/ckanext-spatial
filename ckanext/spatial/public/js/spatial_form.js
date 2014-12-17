/* Module to capture a drawn polygon
 * Based on dataset_map.js with ideas from spatial_query.js
 */
this.ckan.module('spatial-form', function (jQuery, _) {

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
      this.input_id = this.el.data('input_id');
      this.map_id = 'dataset-map-container';

      // hack to make leaflet use a particular location to look for images
      L.Icon.Default.imagePath = this.options.site_url + 'js/vendor/leaflet/images';

      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);

    },

    _onReady: function(){

      var map, backgroundLayer, extentLayer, ckanIcon;

      map = ckan.commonLeafletMap(
        this.map_id,
        //this.options.map_config, 
        {attributionControl: false}
      );

      if (!this.extent) {
          //return false;
          /* create = no polygon defined yet  */
      } else {
          /* update = show existing polygon */
          var extentLayer = L.geoJson(this.extent, {
              style: this.options.styles.default_,
              pointToLayer: function (feature, latLng) {
                return new L.Marker(latLng, {icon: new ckanIcon})
              }});
          extentLayer.addTo(map);
          map.fitBounds(extentLayer.getBounds());
      }

      var ckanIcon = L.Icon.extend({options: this.options.styles.point});

    /* add draw polygon controls */
    /* add event listener on polygon drawn to update input_id with geometry */
    }
  }
});
