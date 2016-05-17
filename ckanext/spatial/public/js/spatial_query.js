/* Module for handling the spatial querying
 */
this.ckan.module('spatial-query', function ($, _) {

  L.Control.Arrow = L.Control.extend({
    options: {
      position: 'topleft'
    },

    onAdd: function (map) {
      var arrowName = 'leaflet-control-arrow',
          barName = 'leaflet-bar',
          partName = barName + '-part',
          container = L.DomUtil.create('div', arrowName + ' ' + barName);

      this._map = map;

      this._moveUpButton = this._createButton('', 'Move up',
              arrowName + '-up ' +
              partName + ' ' +
              partName + '-up',
              container, this._move('up'), this);

      this._moveLeftButton = this._createButton('', 'Move left',
              arrowName + '-left ' +
              partName + ' ' +
              partName + '-left',
              container, this._move('left'),  this);

      this._moveRightButton = this._createButton('', 'Move right',
              arrowName + '-right ' +
              partName + ' ' +
              partName + '-right',
              container, this._move('right'), this);

      this._moveDownButton = this._createButton('', 'Move down',
              arrowName + '-down ' +
              partName + ' ' +
              partName + '-down',
              container, this._move('down'), this);


      return container;
    },

    onRemove: function (map) {

    },

    _move: function (direction) {
      var d = [0, 0];
      var self = this;

      switch (direction){
        case 'up':
          d[1] = -10;
          break;
        case 'down':
          d[1] = 10;
          break;
        case 'left':
          d[0] = -10;
          break;
        case 'right':
          d[0] = 10;
          break;
      }
      return function(e){
        self._map.panBy(d);
      }
    },

    _createButton: function (html, title, className, container, fn, context) {
      var link = L.DomUtil.create('a', className, container);
      link.innerHTML = html;
      link.href = '#';
      link.title = title;

      var stop = L.DomEvent.stopPropagation;

      L.DomEvent
          .on(link, 'click', stop)
          .on(link, 'mousedown', stop)
          .on(link, 'dblclick', stop)
          .on(link, 'click', L.DomEvent.preventDefault)
          .on(link, 'click', fn, context);

      return link;
    }
  });




  return {
    options: {
      i18n: {
      },
      style: {
        color: '#F06F64',
        weight: 2,
        opacity: 1,
        fillColor: '#F06F64',
        fillOpacity: 0.1
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
          this.options.default_extent = user_default_extent;
        } else if (user_default_extent instanceof Object) {
          // Assume it's a GeoJSON bbox
          this.options.default_extent = new L.GeoJSON(user_default_extent).getBounds();
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
      var is_exanded = false;
      var should_zoom = true;
      var form = $("#dataset-search");
      var map_attribution = $('#dataset-map-attribution');
      var map_nav = $('#dataset-map-nav');
      var show_map_link = $('.show-map-link', map_nav);
      // CKAN 2.1
      if (!form.length) {
          form = $(".search-form");
      }
      var aFields = ['west-lng', 'north-lat', 'east-lng', 'south-lat'];
      var aForm = [];
      for (var f in aFields){
        aForm.push($('#' + aFields[f]));
      }

      var buttons;

      var jqaForm = $();  // empty jQuery object
      $.each(aForm, function(i, o) {jqaForm = jqaForm.add(o)});
      jqaForm.on('change', function(e){
        $(e.target).next().text(parseFloat(e.target.value, 5).toFixed(1));
      })

      // Add necessary fields to the search form if not already created
      $(['ext_bbox', 'ext_prev_extent']).each(function(index, item){
        if ($("#" + item).length === 0) {
          $('<input type="hidden" />').attr({'id': item, 'name': item}).appendTo(form);
        }
      });

      // OK map time
      map = ckan.commonLeafletMap('dataset-map-container', this.options.map_config, {attributionControl: false});

      // Initialize the draw control
      map.addControl(new L.Control.Draw({
        position: 'topright',
        polyline: false, polygon: false,
        circle: false, marker: false,
        rectangle: {
          shapeOptions: module.options.style,
          title: 'Draw rectangle'
        }
      }));
      map.addControl(new L.Control.Arrow());

      // OK add the expander
      $('.leaflet-control-draw a', module.el)
        .add($('.show-map-link', map_nav))
        .on('click', function(e) {
        if (!is_exanded) {
          map_nav.hide();
          $('body').addClass('dataset-map-expanded');
          if (should_zoom && !extentLayer) {
            map.zoomIn();
          }
          resetMap();
          is_exanded = true;
        }
      });
      $('.show-map-link i', map_nav).on('click', function(e){
        window.location.href = $('#dataset-map-clear').attr('href');
        e.stopPropagation();
      });

      $('.extended-map-show-form a', module.el).on('click', toggleCoordinateForm);

      // Setup the expanded buttons
      buttons = $(module.template.buttons).insertBefore(map_attribution);

      // Handle the cancel expanded action
      $('.cancel', buttons).on('click', function() {
        map_nav.show();
        $('body').removeClass('dataset-map-expanded');
        resetBBox();
        resetMap();
        is_exanded = false;
      });

      // Handle the apply expanded action
      $('.apply', buttons).on('click', function() {
        if (extentLayer) {
          $('body').removeClass('dataset-map-expanded');
          is_exanded = false;
          resetMap();
          // Eugh, hacky hack.
          setTimeout(function() {
            map.fitBounds(extentLayer.getBounds());
            submitForm();
          }, 200);
        }
      });

      $('#extended-map-reset').on('click', resetBBox);
      $('#extended-map-update').on('click', function(){
        var c = [];
        for (var i in aForm){
          c.push(aForm[i].val());
        }
        if (c.every(function(e){
          return e.length;
        })){
          var rect = new L.Rectangle(
            new L.LatLngBounds(L.latLng(c[3], c[0]), L.latLng(c[1], c[2])),
            module.options.style
          );

          drawRect(rect);
        }
      });

      // When user finishes drawing the box, record it and add it to the map
      map.on('draw:rectangle-created', function (e) {
        bbox_preparations();

        drawRect(e.rect);
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

      function resetBBox() {
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        drawBBox(map.getBounds().toBBoxString());
      }

      function drawRect(rect) {
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        extentLayer = rect;
        var bbox_string = extentLayer.getBounds().toBBoxString();
        $('#ext_bbox').val(bbox_string);
        fillForm(bbox_string);
        map.addLayer(extentLayer);
        map.fitBounds(extentLayer.getBounds());
        $('.apply', buttons).removeClass('disabled').addClass('btn-primary');
      }

      // Is there an existing box from a previous search?
      function setPreviousBBBox() {
        previous_bbox = module._getParameterByName('ext_bbox');
        if (previous_bbox) {
          bbox_preparations();
          drawBBox(previous_bbox);
        } else {
          fillForm(null);
        }
      }

      function drawBBox(bbox) {
        $('#ext_bbox').val(bbox);
        extentLayer = module._drawExtentFromCoords(bbox.split(','))
        fillForm(bbox);
        map.addLayer(extentLayer);
        map.fitBounds(extentLayer.getBounds());
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

      function bbox_preparations() {
        $('body').addClass('dataset-map-layer-drawn')
        show_map_link.parent().addClass('active');
      }

      function toggleCoordinateForm(event) {
        $(event.target).toggleClass('active').parent().toggleClass('active')
      }

      function fillForm(bounds){
        if (bounds === null) {
          $('.extended-map-form input').val('');
          return;
        }
        var b = $.map(bounds.split(','), function(e){
          return parseFloat(e).toFixed(1)
        })

        for (var i in b){
          aForm[i].val(b[i]).trigger('change');
        }

      }

    }
  }
});
