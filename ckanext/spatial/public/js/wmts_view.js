// wmts preview module
ckan.module('wmtspreview', function (jQuery, _) {
  return {
    initialize: function () {
      var self = this;

      self.el.empty();
      self.el.append($("<div></div>").attr("id","map"));
      self.map = ckan.commonLeafletMap('map', this.options.map_config, {center: [0, 0], zoom: 3});

      $.ajaxSetup({
        beforeSend: function (xhr) {
          xhr.overrideMimeType("application/xml; charset=UTF-8");
        }
      });

      // use CORS, if supported by browser and server
      if (jQuery.support.cors && preload_resource['original_url'] !== undefined) {
        jQuery.get(preload_resource['original_url'])
        .done(
          function(data){
            self.showPreview(preload_resource['original_url'], data);
          })
        .fail(
          function(jqxhr, textStatus, error) {
            jQuery.get(preload_resource['url']).done(
              function(data){
                self.showPreview(preload_resource['original_url'], data);
              })
            .fail(
              function(jqXHR, textStatus, errorThrown) {
                self.showError(jqXHR, textStatus, errorThrown);
              }
            );
          }
        );
      } else {
        jQuery.get(preload_resource['url']).done(
          function(data){
            self.showPreview(preload_resource['original_url'], data);
          })
        .fail(
          function(jqXHR, textStatus, errorThrown) {
            self.showError(jqXHR, textStatus, errorThrown);
          }
        );
      }
    },

    showError: function (jqXHR, textStatus, errorThrown) {
      if (textStatus == 'error' && jqXHR.responseText.length) {
        this.el.html(jqXHR.responseText);
      } else {
        this.el.html(this.i18n('error', {text: textStatus, error: errorThrown}));
      }
    },

    showPreview: function (url, data) {
      var self = this;
      var map_ids = [], map_titles = [], maps = {};
      var namespace = "ows\\:"; // Most prefer this...
      var xml_map_ids = $(data).find("Contents Layer > " + namespace + "Identifier");
      var xml_map_titles = $(data).find("Contents Layer > " + namespace + "Title");
      if( xml_map_ids.length == 0 ) {
        namespace = ""; // ...but some don't!
        xml_map_ids = $(data).find("Contents Layer > " + namespace + "Identifier");
        xml_map_titles = $(data).find("Contents Layer > " + namespace + "Title");
      }
      for (var i=0, max=xml_map_ids.length; i < max; i++) {
        map_ids.push(xml_map_ids[i].textContent);
        map_titles.push(xml_map_titles[i].textContent);
      }
      for (var i=0, max=map_ids.length; i < max; i++) {
        maps[map_titles[i]] = L.tileLayer(url + "&REQUEST=GetTile&VERSION=1.0.0&LAYER=" + map_ids[i] + "&STYLE=_null&TILEMATRIXSET=GoogleMapsCompatible&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&FORMAT=image/png");
      }
      self.map.addLayer(maps[map_titles[0]]);
      L.control.layers(maps, null).addTo(self.map);
      L.control.coordinates({
        labelTemplateLat:"Latitude: {y}",
        labelTemplateLng:"Longitude: {x}",
        useLatLngOrder: true
      }).addTo(self.map);
    }
  };
});
