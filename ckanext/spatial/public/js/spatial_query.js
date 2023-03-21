/* Module for handling the spatial querying
 */
this.ckan.module('spatial-query', function ($, _) {

  return {
    options: {
      i18n: {},
      style: {
        color: "#F06F64",
        weight: 2,
        opacity: 1,
        fillColor: "#F06F64",
        fillOpacity: 0.1,
        clickable: false,
      },
      default_extent: [
        [90, 180],
        [-90, -180],
      ],
    },
    template: {
      buttons: [
        '<div id="dataset-map-edit-buttons">',
        '<a href="javascript:;" class="btn cancel">Cancel</a> ',
        '<a href="javascript:;" class="btn apply disabled">Apply</a>',
        "</div>",
      ].join(""),
    },

    initialize: function () {
      var module = this;
      $.proxyAll(this, /_on/);

      var user_default_extent = this.el.data("default_extent");
      if (user_default_extent) {
        if (user_default_extent instanceof Array) {
          // Assume it's a pair of coords like [[90, 180], [-90, -180]]
          module.options.default_extent = user_default_extent;
        } else if (user_default_extent instanceof Object) {
          // Assume it's a GeoJSON bbox
          module.options.default_extent = new L.GeoJSON(
            user_default_extent
          ).getBounds();
        }
      }
      this.el.ready(this._onReady);
    },

    _getParameterByName: function (name) {
      var url = new URL(window.location.href);
      var search_params = url.searchParams;
      return search_params.get(name);
    },

    _removeParameterByName: function (name) {
      var url = new URL(window.location.href);
      var search_params = url.searchParams;
      search_params.delete(name);
      url.search = search_params.toString();
      window.history.pushState({}, "", url.toString());
    },

    _drawExtentFromCoords: function (xmin, ymin, xmax, ymax) {
      if ($.isArray(xmin)) {
        var coords = xmin;
        xmin = coords[0];
        ymin = coords[1];
        xmax = coords[2];
        ymax = coords[3];
      }
      return new L.Rectangle(
        [
          [ymin, xmin],
          [ymax, xmax],
        ],
        this.options.style
      );
    },

    _drawExtentFromGeoJSON: function (geom) {
      return new L.GeoJSON(geom, { style: this.options.style });
    },

    _onReady: function () {
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
      $(["ext_bbox", "ext_prev_extent", "ext_layers"]).each(function (index, item) {
        if ($("#" + item).length === 0) {
          $('<input type="hidden" />')
            .attr({ id: item, name: item })
            .appendTo(form);
        }
      });

      // OK map time
      map = ckan.commonLeafletMap(
        "dataset-map-container",
        module.options.map_config,
        {
          attributionControl: false,
          drawControlTooltips: false,
          fullscreenControl: true,
          fullscreenControlOptions: {
            position: "topleft",
          },
        }
      );

      // Initialize the draw control
      map.addControl(
        new L.Control.Draw({
          position: "topright",
          draw: {
            polyline: false,
            polygon: false,
            circle: false,
            marker: false,
            circlemarker: false,
            rectangle: { shapeOptions: module.options.style },
          },
        })
      );

      L.Control.RemoveAll = L.Control.extend({
        options: {
          position: "topright",
        },
        onAdd: function (map) {
          var controlDiv = L.DomUtil.create(
            "div",
            "leaflet-draw-toolbar leaflet-bar"
          );
          L.DomEvent.addListener(
            controlDiv,
            "click",
            L.DomEvent.stopPropagation
          )
            .addListener(controlDiv, "click", L.DomEvent.preventDefault)
            .addListener(controlDiv, "click", function () {
              if (extentLayer) {
                map.removeLayer(extentLayer);
                var url = new URL(window.location.href);
                var search_params = url.searchParams;
                search_params.delete("ext_bbox");
                search_params.delete("ext_location");
                url.search = search_params.toString();
                window.location.href = url.toString();
              }
            });

          var controlUI = L.DomUtil.create(
            "a",
            "leaflet-draw-edit-remove",
            controlDiv
          );
          controlUI.title = "Clear";
          controlUI.href = "#";
          return controlDiv;
        },
      });
      var removeAllControl = new L.Control.RemoveAll();
      map.addControl(removeAllControl);

      var features = this.el.data("dataset_extents");

      var orangeIcon = new L.Icon({
        iconUrl:
          "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
        shadowUrl:
          "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
        iconSize: [12, 21],
        iconAnchor: [6, 21],
        popupAnchor: [1, -34],
        shadowSize: [21, 21],
      });

      module.options.dataset_extents = new L.geoJSON(features, {
        style: {
          color: "#fab700",
          weight: 2,
          opacity: 0.8,
          fillColor: "#33a02c",
          fillOpacity: 0,
          clickable: false,
        },
        pointToLayer: function (feature, latlng) {
          if (feature.geometry.type == "Point") {
            return L.marker(latlng, { icon: orangeIcon });
          }
          return;
        },
        // onEachFeature: function (feature, layer) {
        //   if(feature.properties && feature.properties.title){
        //     layer.bindPopup(feature.properties.title);
        //   }
        // }
      });

      if (module._getParameterByName("ext_layers") == "dataset_extents") {
        $("#ext_layers").val("dataset_extents");
        map.fitBounds(module.options.default_extent);
        map.addLayer(module.options.dataset_extents);
      }

      var layerControl = new L.control.layers(null, null, { collapsed: true })
        .addOverlay(
          module.options.dataset_extents,
          "<span>Dataset Extents</span>"
        )
        .setPosition("topleft")
        .addTo(map);   

      map.on("overlayadd", function (ev) {
        if (ev["name"].includes("Dataset Extents")) {
          $("#ext_layers").val("dataset_extents");
        }
      });

      map.on("overlayremove", function (ev) {
        if (ev["name"].includes("Dataset Extents")) {
          $("#ext_layers").val("");
        }
      });

      // map.on("enterFullscreen", function () {
      //   map.addControl(layerControl);
      // });

      // map.on("exitFullscreen", function () {
      //   //map.removeLayer(module.options.dataset_extents);
      //   map.removeControl(layerControl);
      // });

      // When user finishes drawing the box, record it and add it to the map
      map.on("draw:created", function (e) {
        if (extentLayer) {
          map.removeLayer(extentLayer);
        }
        extentLayer = e.layer;
        $("#ext_bbox").val(extentLayer.getBounds().toBBoxString());
        map.addLayer(extentLayer);
        if (
          String(module.options.spatial_widget_expands).toLowerCase() === "true"
        ) {
          $(".apply", buttons).removeClass("disabled").addClass("btn-primary");
        } else {
          // Eugh, hacky hack. but submitts the query as there is no apply button
          setTimeout(function () {
            map.fitBounds(extentLayer.getBounds());
            submitForm();
          }, 200);
        }
      });

      // Record the current map view so we can replicate it after submitting
      map.on("moveend", function (e) {
        $("#ext_prev_extent").val(map.getBounds().toBBoxString());
      });

      // Ok setup the default state for the map
      var previous_bbox;
      setPreviousBBBox();
      setPreviousExtent();

      // OK, when we expand we shouldn't zoom then
      map.on("zoomstart", function (e) {
        should_zoom = false;
      });

      // Is there an existing box from a previous search?
      function setPreviousBBBox() {
        previous_bbox = module._getParameterByName("ext_bbox");
        if (previous_bbox) {
          $("#ext_bbox").val(previous_bbox);
          extentLayer = module._drawExtentFromCoords(previous_bbox.split(","));
          map.addLayer(extentLayer);
          map.fitBounds(extentLayer.getBounds());
        }
      }

      // Is there an existing extent from a previous search?
      function setPreviousExtent() {
        previous_extent = module._getParameterByName("ext_prev_extent");
        if (previous_extent) {
          coords = previous_extent.split(",");
          map.fitBounds([
            [coords[1], coords[0]],
            [coords[3], coords[2]],
          ]);
          module._removeParameterByName("ext_prev_extent");
        } else {
          if (!previous_bbox) {
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
        setTimeout(function () {
          form.submit();
        }, 800);
      }
    },
  };
});
