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
      ].join(''),
      modal: [
        '<div class="modal">',
        '<div class="modal-dialog modal-lg">',
        '<div class="modal-content">',
        '<div class="modal-header">',
        '<button type="button" class="close" data-dismiss="modal">×</button>',
        '<h3 class="modal-title"></h3>',
        '</div>',
        '<div class="modal-body"><div id="draw-map-container"></div></div>',
        '<div class="modal-footer">',
        '<button class="btn btn-default btn-cancel" data-dismiss="modal"></button>',
        '<button class="btn apply btn-primary disabled"></button>',
        '</div>',
        '</div>',
        '</div>',
        '</div>'
      ].join('\n')

    },

    initialize: function () {
      var module = this;
      $.proxyAll(this, /_on/);

      var user_default_extent = this.el.data('default_extent');
      if (user_default_extent ){
        if (user_default_extent instanceof Array) {
          // Assume it's a pair of coords like [[90, 180], [-90, -180]]
          this.options.default_extent = user_default_extent;
        } else if (user_default_extent instanceof Object) {
          // Assume it's a GeoJSON bbox
          this.options.default_extent = new L.GeoJSON(user_default_extent).getBounds();
        }
      }
      this.el.ready(this._onReady);
    },

    _createModal: function () {
      if (!this.modal) {
        var element = this.modal = jQuery(this.template.modal);
        element.on('click', '.btn-primary', this._onApply);
        element.on('click', '.btn-cancel', this._onCancel);
        element.modal({show: false});

        element.find('.modal-title').text(this._('Please draw the extent to query:'));
        element.find('.btn-primary').text(this._('Apply'));
        element.find('.btn-cancel').text(this._('Cancel'));

        var module = this;

        this.modal.on('shown.bs.modal', function () {
          if (module.drawMap) {
            module._setPreviousBBBox(map, zoom=false);

            // TODO
            $('a.leaflet-draw-draw-rectangle', element).trigger('click');
            return
          }
          var container = element.find('#draw-map-container')[0];
          module.drawMap = map = module._createMap(container);

          // Initialize the draw control
          var draw = new L.Control.Draw({
            position: 'topright',
            draw: {
              polyline: false,
              polygon: false,
              circle: false,
              circlemarker: false,
              marker: false,
              rectangle: {shapeOptions: module.options.style}
            }
          });

          map.addControl(draw);

          module._setPreviousBBBox(map, zoom=false);
          map.fitBounds(module.mainMap.getBounds());

          if (map.getZoom() == 0) {
            map.zoomIn();
          }

          map.on('draw:created', function (e) {
            if (module.extentLayer) {
              map.removeLayer(module.extentLayer);
            }
            module.extentLayer = extentLayer = e.layer;
            $('#ext_bbox').val(extentLayer.getBounds().toBBoxString());
            map.addLayer(extentLayer);
            element.find('.btn-primary').removeClass('disabled').addClass('btn-primary');
          });

          // Record the current map view so we can replicate it after submitting
          map.on('moveend', function(e) {
            $('#ext_prev_extent').val(map.getBounds().toBBoxString());
          });

          // TODO
          $('a.leaflet-draw-draw-rectangle', element).trigger('click');

        })

        this.modal.on('hidden.bs.modal', function () {
          module._onCancel()
        });

      }
      return this.modal;
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

    _onApply: function() {
      $(".search-form").submit();
    },

    _onCancel: function() {
      if (this.extentLayer) {
        this.drawMap.removeLayer(this.extentLayer);
      }
    },

    _createMap: function(container) {
      map = ckan.commonLeafletMap(
        container,
        this.options.map_config,
        {
          attributionControl: false,
          drawControlTooltips: false
        }
      );

      return map;

    },

    // Is there an existing box from a previous search?
    _setPreviousBBBox: function(map, zoom=true) {
      previous_bbox = this._getParameterByName('ext_bbox');
      if (previous_bbox) {
        $('#ext_bbox').val(previous_bbox);
        this.extentLayer = this._drawExtentFromCoords(previous_bbox.split(','))
        map.addLayer(this.extentLayer);
        if (zoom) {
          map.fitBounds(this.extentLayer.getBounds());
        }
      }
    },

    // Is there an existing extent from a previous search?
    _setPreviousExtent: function(map) {
      previous_extent = this._getParameterByName('ext_prev_extent');
      if (previous_extent) {
        coords = previous_extent.split(',');
        map.fitBounds([[coords[1], coords[0]], [coords[3], coords[2]]], {"animate": false});
      } else {
        if (!previous_bbox){
            map.fitBounds(this.options.default_extent, {"animate": false});
        }
      }
    },

    _onReady: function() {
      var module = this;
      var map;
      var extentLayer;
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
      this.mainMap = map = this._createMap('dataset-map-container');

      // OK add the expander
      var module = this;

      var expandButton = L.Control.extend({
        position: 'topright',
        onAdd: function(map) {
          var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');

          var button = L.DomUtil.create('a', 'leaflet-control-custom-button', container);
          button.innerHTML = '<i class="fa fa-pencil"></i>';
          button.title = module._('Draw an extent');

          L.DomEvent.on(button, 'click', function(e) {
            module.sandbox.body.append(module._createModal());
            module.modal.modal('show');

          });

          return container;
        }
      });
      map.addControl(new expandButton());


      // When user finishes drawing the box, record it and add it to the map
      map.on('draw:created', function (e) {
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        extentLayer = e.layer;
        $('#ext_bbox').val(extentLayer.getBounds().toBBoxString());
        map.addLayer(extentLayer);
        $('.apply', buttons).removeClass('disabled').addClass('btn-primary');
      });

      // Record the current map view so we can replicate it after submitting
      map.on('moveend', function(e) {
        $('#ext_prev_extent').val(map.getBounds().toBBoxString());
      });

      module._setPreviousBBBox(map);
      module._setPreviousExtent(map);

    }
  }
});
