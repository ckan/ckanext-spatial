/* Module providing a map widget to display, edit, or capture a GeoJSON polygon geometry
 * Based on dataset_map.js with ideas from spatial_query.js
 *
 * Usage:
 * In your form snippet / template, embed a map as follows above an input {{ id }} which
 * accepts a GeoJSON geometry (e.g. the field "spatial" for the dataset extent):

    {% set map_config = h.get_common_map_config() %}
    <div class="dataset-map" 
        data-module="spatial-form"
        data-input_id="{{ id }}"
        data-extent="{{ value }}" 
        data-module-site_url="{{ h.dump_json(h.url('/', locale='default', qualified=true)) }}" 
        data-module-map_config="{{ h.dump_json(map_config) }}">
      <div id="dataset-map-container"></div>
    </div>

    {% resource 'ckanext-spatial/spatial_form' %}

 * {{ id }} is the id of the form input to be updated with what you draw on the map
 * {{ value }} is an existing GeoJSON geometry to be shown (editable, deletable) on the map
 * This module will replace the div shown above with:
 * - a map showing the GeoJSON geometry given as {{ value }} if existing
 * - a button "text to map", which overwrites the map with the GeoJSON geometry inside input {{ id }}
 * - a button "map to text", which overwrites the input {{ id }} with the GeoJSON geometry on the map
 * - this module loaded, providing the binding between map and form input
 * 
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
          weight: 1,
          opacity: 1,
          fillColor: '#FCF6CF',
          fillOpacity: 0.4
        }
      }
    },

    initialize: function () {

      this.input_id = this.el.data('input_id');
      this.extent = this.el.data('extent');
      this.map_id = 'dataset-map-container'; //-' + this.input_id;

      // hack to make leaflet use a particular location to look for images
      L.Icon.Default.imagePath = this.options.site_url + 'js/vendor/leaflet/images';

      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);

    },

    _onReady: function(){

        var map, backgroundLayer, extentLayer, ckanIcon;
        var ckanIcon = L.Icon.extend({options: this.options.styles.point});

        /* Initialise basic map */
        map = ckan.commonLeafletMap(
            this.map_id,
            this.options.map_config, 
            {attributionControl: false}
        );

        /* Add existing extent or new layer */
        if (!this.extent) {
            /* create = no polygon defined yet  */
            var drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);
        } else {
            /* update = show existing polygon */
            var drawnItems = L.geoJson(this.extent, {
            style: this.options.styles.default_,
            pointToLayer: function (feature, latLng) {
                return new L.Marker(latLng, {icon: new ckanIcon})
            }});
            drawnItems.addTo(map);
            map.fitBounds(drawnItems.getBounds());
        }

        /* Leaflet.draw: add drawing controls for drawnItems */
        var drawControl = new L.Control.Draw({
            edit: { featureGroup: drawnItems },
            marker: false,
            polyline: false,
            polygon: true,
            rectangle: true,
            circle: false
        });
        map.addControl(drawControl);

        /* add event listener on polygon drawn to update input_id with geometry */
        map.on('draw:created', function (e) {
            var type = e.layerType,
            layer = e.layer;

            alert("pretend we're updating the textarea")

            // Do whatever else you need to. (save to db, add to map etc)
            drawnItems.addLayer(layer);
        });


    }
  }
});
