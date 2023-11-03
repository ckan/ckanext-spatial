/* Code based on work by Florian Mayer https://github.com/florianm/ckanext-spatial/blob/master/ckanext/spatial/public/js/spatial_form.js
 * Modified by Matthew Foster and others from CIOOS-SIOOC
*/
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
      table: '<table class="table table-striped table-bordered table-condensed"><tbody>{body}</tbody></table>',
      row: '<tr><th>{key}</th><td>{value}</td></tr>',
      i18n: {
      },
      styles: {
        point:{
          iconUrl: '/js/vendor/leaflet/images/marker-icon.png',
          iconSize: [14, 25],
          iconAnchor: [7, 25]
        },
        default_:{
          color: '#B52',
          weight: 1,
          opacity: 1,
          fillColor: '#FCF6CF',
          fillOpacity: 0.4
        },
      },
      default_extent: [[48.0, -130.0], [60.0, -110.0]]
    },


    initialize: function () {

      this.ids = this.el.data('input_ids');
      this.extent = this.el.data('extent');
      this.map_id = 'dataset-map-form-container';

      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);

    },


    _onReady: function(){

      var map, backgroundLayer, oldExtent, drawnItems, ckanIcon;
      var ckanIcon = L.Icon.extend({ options: this.options.styles.point });

      var _self = this; // used in event handlers as this points to dom object in that case

      /* Initialise basic map */
      map = ckan.commonLeafletMap(
        this.map_id,
        this.options.map_config,
        { attributionControl: false }
      );
      map.fitBounds(this.options.default_extent);

      /* Add an empty layer for newly drawn items */
      var drawnItems = new L.FeatureGroup();
      map.addLayer(drawnItems);


      /* Add existing extent or new layer */
      if (this.extent) {
        L.geoJson(this.extent, {
          style: this.options.styles.default_,
          pointToLayer: function (feature, latLng) {
            return new L.Marker(latLng, { icon: new ckanIcon })
          }
        }).eachLayer(function (layer) {
          drawnItems.addLayer(layer);
        });

        map.fitBounds(drawnItems.getBounds());
      }


        /* Leaflet.draw: add drawing controls for drawnItems */
      map.addControl(new L.Control.Draw({
        position: "topright",
        draw: {
          polyline: false,
          polygon: true,
          circle: false,
          marker: true,
          circlemarker: false,
          rectangle: true

        },
        edit: {
          featureGroup: drawnItems
        }

      })
      );


      /* populate form fields from gemoetry drawn on map */
        var featureGroupToInput = function(fg, input){
          var gj = drawnItems.toGeoJSON().features;
          var geom = null;
          $.each(gj, function (index, value) {
            if (value.geometry.type == "FeatureCollection") {
              geom = value.geometry.features[0].geometry
            } else {
              geom = value.geometry
            }
          });

          if (geom) {
            mp = { "type": geom.type, "coordinates": geom.coordinates };
            $('#' + input).val(JSON.stringify(mp));
          } else {
            $('#' + input).val('');
          }

          var bounds = drawnItems.getBounds();
          if (bounds._southWest && bounds._northEast) {
            $("#" + _self.ids['bbox-north']).val(+bounds.getNorth().toFixed(7));
            $("#" + _self.ids['bbox-south']).val(+bounds.getSouth().toFixed(7));
            $("#" + _self.ids['bbox-east']).val(+bounds.getEast().toFixed(7));
            $("#" + _self.ids['bbox-west']).val(+bounds.getWest().toFixed(7));
          }
        };

        // Handle the update map action
        $('#update_spatial_form_map').on('click', function() {
          drawnItems.clearLayers();
          var jsonStr = $('#' + _self.ids['spatial']).val();
          if(jsonStr){
            L.geoJson(JSON.parse(jsonStr)).eachLayer(function (layer) {
              drawnItems.addLayer(layer);
            });
            var bounds = drawnItems.getBounds();
            if(bounds._southWest && bounds._northEast){
              $("#" + _self.ids['bbox-north']).val(+bounds.getNorth().toFixed(7));
              $("#" + _self.ids['bbox-south']).val(+bounds.getSouth().toFixed(7));
              $("#" + _self.ids['bbox-east']).val(+bounds.getEast().toFixed(7));
              $("#" + _self.ids['bbox-west']).val(+bounds.getWest().toFixed(7));
            }
          }
        });

        // Handle the clear map action
        $('#clear_spatial_form').on('click', function() {
          drawnItems.clearLayers();
          $("#" + _self.ids['spatial']).val('');
          $("#" + _self.ids['bbox-north']).val('');
          $("#" + _self.ids['bbox-south']).val('');
          $("#" + _self.ids['bbox-east']).val('');
          $("#" + _self.ids['bbox-west']).val('');
        });

        /* When one shape is drawn/edited/deleted, update input_id with all drawn shapes */
        map.on('draw:created', function (e) {
            var type = e.layerType,
                layer = e.layer;
          drawnItems.addLayer(layer);
            featureGroupToInput(drawnItems, _self.ids['spatial']);
        });

        map.on('draw:editstop', function(e){
            featureGroupToInput(drawnItems, _self.ids['spatial']);
        });

        map.on('draw:deletestop', function(e){
            featureGroupToInput(drawnItems, _self.ids['spatial']);
        });

    }
  }
});
