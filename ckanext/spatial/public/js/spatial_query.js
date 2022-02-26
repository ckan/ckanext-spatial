/* Module for handling the spatial querying
 */
this.ckan.module('spatial-query', function ($, _) {

  return {
    options: {
      i18n: {
      },
      style: {
        color: '#F06F64',
        weight: 2,
        opacity: 1,
        fillColor: '#F06F64',
        fillOpacity: 0.1,
        clickable: false
      },
      default_extent: [[90, 180], [-90, -180]]
    },
    template: {
      buttons: [
        '<div id="dataset-map-edit-buttons">',
        '<a href="javascript:;" class="btn cancel">Cancel</a> ',
        '<a href="javascript:;" class="btn apply disabled">Apply</a>',
        '</div>'
      ].join('')
    },

    initialize: function () {
      var module = this;
      $.proxyAll(this, /_on/);

      var user_default_extent = this.el.data('default_extent');
      if (user_default_extent ){
        if (user_default_extent instanceof Array) {
          // Assume it's a pair of coords like [[90, 180], [-90, -180]]
          module.options.default_extent = user_default_extent;
        } else if (user_default_extent instanceof Object) {
          // Assume it's a GeoJSON bbox
          module.options.default_extent = new L.GeoJSON(user_default_extent).getBounds();
        }
      }
      this.el.ready(this._onReady);
    },

    _getParameterByName: function (name) {
      var match = RegExp('[?&]' + name + '=([^&]*)')
                        .exec(window.location.search);
      return match ?
          decodeURIComponent(match[1].replace(/\+/g, ' '))
          : null;
    },

    _drawExtentFromCoords: function(xmin, ymin, xmax, ymax) {
        if ($.isArray(xmin)) {
            var coords = xmin;
            xmin = coords[0]; ymin = coords[1]; xmax = coords[2]; ymax = coords[3];
        }
        return new L.Rectangle([[ymin, xmin], [ymax, xmax]],
                               this.options.style);
    },

    _drawExtentFromGeoJSON: function(geom) {
        return new L.GeoJSON(geom, {style: this.options.style});
    },

    _onReady: function() {
      var module = this;
      var map;
      var extentLayer;
      var previous_box;
      var previous_extent;
      var is_expanded = false;
      var should_zoom = true;
      var form = $("#dataset-search");

      // CKAN 2.1
      if (!form.length) {
          form = $(".search-form");
      }

      var buttons;

      // Add necessary fields to the search form if not already created
      $(['ext_bbox', 'ext_prev_extent']).each(function(index, item){
        if ($("#" + item).length === 0) {
          $('<input type="hidden" />').attr({'id': item, 'name': item}).appendTo(form);
        }
      });

      // OK map time
      map = ckan.commonLeafletMap(
        'dataset-map-container',
        module.options.map_config,
        {
          attributionControl: false,
          drawControlTooltips: false,
          fullscreenControl: true,
          fullscreenControlOptions: {
            position: 'topleft'
          }
        }
      );

      // Initialize the draw control
      map.addControl(new L.Control.Draw({
        position: 'topright',
        draw: {
          polyline: false,
          polygon: false,
          circle: false,
          marker: false,
          circlemarker: false,
          rectangle: {shapeOptions: module.options.style}
        }
      }));

      L.Control.RemoveAll = L.Control.extend(
      {
          options:
          {
              position: 'topright',
          },
          onAdd: function (map) {
              var controlDiv = L.DomUtil.create('div', 'leaflet-draw-toolbar leaflet-bar');
              L.DomEvent
                  .addListener(controlDiv, 'click', L.DomEvent.stopPropagation)
                  .addListener(controlDiv, 'click', L.DomEvent.preventDefault)
                  .addListener(controlDiv, 'click', function () {
                  if (extentLayer) {
                    map.removeLayer(extentLayer);
                    var url = new URL(window.location.href);
                    var search_params = url.searchParams;
                    search_params.delete('ext_bbox');
                    search_params.delete('ext_prev_extent');
                    search_params.delete('ext_location');
                    url.search = search_params.toString();
                    window.location.href = url.toString();
                  }
              });

              var controlUI = L.DomUtil.create('a', 'leaflet-draw-edit-remove', controlDiv);
              controlUI.title = 'Clear';
              controlUI.href = '#';
              return controlDiv;
          }
      });
      var removeAllControl = new L.Control.RemoveAll();
      map.addControl(removeAllControl);

      // OK add the expander
      $('a.leaflet-draw-draw-rectangle', module.el).on('click', function(e) {
        if (!is_expanded && String(module.options.spatial_widget_expands).toLowerCase() === 'true') {
          $('body').addClass('dataset-map-expanded');
          if (should_zoom && !extentLayer) {
            map.zoomIn();
          }
          resetMap();
          is_expanded = true;
        }
      });

      // Setup the expanded buttons
      buttons = $(module.template.buttons).insertBefore('#dataset-map-attribution');

      // Handle the cancel expanded action
      $('.cancel', buttons).on('click', function() {
        $('body').removeClass('dataset-map-expanded');
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        setPreviousExtent();
        setPreviousBBBox();
        resetMap();
        is_expanded = false;
      });

      // Handle the apply expanded action
      $('.apply', buttons).on('click', function() {
        if (extentLayer) {
          $('body').removeClass('dataset-map-expanded');
          is_expanded = false;
          resetMap();
          // Eugh, hacky hack.
          setTimeout(function() {
            map.fitBounds(extentLayer.getBounds());
            submitForm();
          }, 200);
        }
      });

      // When user finishes drawing the box, record it and add it to the map
      map.on('draw:created', function (e) {
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        extentLayer = e.layer;
        $('#ext_bbox').val(extentLayer.getBounds().toBBoxString());
        map.addLayer(extentLayer);
        if (String(module.options.spatial_widget_expands).toLowerCase() === 'true') {
          $('.apply', buttons).removeClass('disabled').addClass('btn-primary');
        } else {
          // Eugh, hacky hack. but submitts the query as there is no apply button
          setTimeout(function() {
            map.fitBounds(extentLayer.getBounds());
            submitForm();
          }, 200);
        }
      });

      // Record the current map view so we can replicate it after submitting
      map.on('moveend', function(e) {
        $('#ext_prev_extent').val(map.getBounds().toBBoxString());
      });

      // Ok setup the default state for the map
      var previous_bbox;
      setPreviousBBBox();
      setPreviousExtent();

      // OK, when we expand we shouldn't zoom then
      map.on('zoomstart', function(e) {
        should_zoom = false;
      });


      // Is there an existing box from a previous search?
      function setPreviousBBBox() {
        previous_bbox = module._getParameterByName('ext_bbox');
        if (previous_bbox) {
          $('#ext_bbox').val(previous_bbox);
          extentLayer = module._drawExtentFromCoords(previous_bbox.split(','))
          map.addLayer(extentLayer);
          map.fitBounds(extentLayer.getBounds());
        }
      }

      // Is there an existing extent from a previous search?
      function setPreviousExtent() {
        previous_extent = module._getParameterByName('ext_prev_extent');
        if (previous_extent) {
          coords = previous_extent.split(',');
          map.fitBounds([[coords[1], coords[0]], [coords[3], coords[2]]]);
        } else {
          if (!previous_bbox){
              map.fitBounds(module.options.default_extent);
          }
        }
      }

      // Reset map view
      function resetMap() {
        L.Util.requestAnimFrame(map.invalidateSize, map, !1, map._container);
      }

      // Add the loading class and submit the form
      function submitForm() {
        setTimeout(function() {
          form.submit();
        }, 800);
      }
    }
  }
});
