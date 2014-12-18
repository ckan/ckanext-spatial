/* Module providing a map widget to display, edit, or capture a GeoJSON polygon geometry
 * Based on dataset_map.js with ideas from spatial_query.js
 *
 * Usage:
 * In your form snippet / template, embed a map as follows above an input {{ id }} which
 * accepts a GeoJSON geometry (e.g. the field "spatial" for the dataset extent):

{% import 'macros/form.html' as form %}

    {% with 
    name=field.field_name, 
    id='field-' + field.field_name,
    label=h.scheming_language_text(field.label),
    placeholder=h.scheming_language_text(field.form_placeholder),
    value=data[field.field_name],
    error=errors[field.field_name],
    classes=['control-medium'],
    is_required=h.scheming_field_required(field)
    %}

    {% call form.input_block(id, label, error, classes, is_required=is_required) %}

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

    {{ form.info(text="Draw the dataset extent on the map,
       or paste a GeoJSON Polygon or Multipolygon geometry below", inline=false) }}

    <textarea id="{{ id }}" type="{{ type }}" name="{{ name }}" 
        placeholder="{{ placeholder }}" rows=10 style="width:100%;">
      {{ value | empty_and_escape }}
    </textarea>

    {% endcall %}
{% endwith %}

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

      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);

    },

    _onReady: function(){

        var map, backgroundLayer, oldExtent, drawnItems, ckanIcon;
        var ckanIcon = L.Icon.extend({options: this.options.styles.point});

        /* Initialise basic map */
        map = ckan.commonLeafletMap(
            this.map_id,
            this.options.map_config, 
            {attributionControl: false}
        );

        /* Add an empty layer for newly drawn items */
        var drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);

        /* TODO add GeoJSON layers for all GeoJSON resources of the dataset */

        /* Add existing extent or new layer */
        if (!this.extent) {
            /* create = no polygon defined yet  */
        } else {
            /* update = show existing polygon */
            oldExtent = L.geoJson(this.extent, {
            style: this.options.styles.default_,
            pointToLayer: function (feature, latLng) {
                return new L.Marker(latLng, {icon: new ckanIcon})
            }});
            //oldExtent.addTo(drawnItems);
            oldExtent.addTo(map);
            map.fitBounds(oldExtent.getBounds());
        }

        /* Leaflet.draw: add drawing controls for drawnItems */
        var drawControl = new L.Control.Draw({
            draw: {
                polyline: false,
                circle: false,
                marker: false,
                rectangle: {repeatMode: false}

            },
            edit: { featureGroup: drawnItems }
        });
        map.addControl(drawControl);

        /* Merge all features in FeatureGroup into one MultiPolygon, update inputid
         * with that Multipolygon's geometry on draw:created, draw:deletestop, draw:editstop
         */
        var featureGroupToInput = function(fg, inputid){
            var gj = drawnItems.toGeoJSON().features;
            var mp = [];
            $.each(gj, function(index, value){ mp.push(value.geometry.coordinates); });
            m = { "type": "MultiPolygon", "coordinates": mp};
            $("#" + inputid)[0].value = JSON.stringify(m);
        };

        /* Update input field #inputid with the GeoJSON geometry of a given feature */
        var layerToInput = function(el, inputid){
            var type = el.layerType,
            layer = el.layer;
            var geojson_geometry = JSON.stringify(layer.toGeoJSON().geometry);
            $("#field-spatial")[0].value = geojson_geometry; 
        };

        /* add event listener on polygon drawn to update input_id with geometry */
        var inputid = this.input_id;
        map.on('draw:created', function (e) {
            var type = e.layerType,
            layer = e.layer;
            drawnItems.addLayer(layer);
            //$("#field-spatial")[0].value = JSON.stringify(e.layer.toGeoJSON().geometry);
            featureGroupToInput(drawnItems, 'field-spatial');
        });

        map.on('draw:editstop', function(e){
            featureGroupToInput(drawnItems, 'field-spatial');
        });

        map.on('draw:deletestop', function(e){
            featureGroupToInput(drawnItems, 'field-spatial');
        });

    }
  }
});
