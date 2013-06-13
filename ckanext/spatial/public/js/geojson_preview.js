// geojson preview module
ckan.module('geojsonpreview', function (jQuery, _) {
  return {
    options: {
    },
    initialize: function () {
      var self = this;

      self.el.empty();
      self.el.append($("<div></div>").attr("id","map"));
      self.map = L.map('map');

      var mapUrl = "http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png";
      var osmAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">';
      var bg = new L.TileLayer(mapUrl, {maxZoom: 18, attribution: osmAttribution, subdomains: '1234'});
      self.map.addLayer(bg);

      // use CORS, if supported by browser and server
      if (jQuery.support.cors && preload_resource['original_url'] !== undefined) {
        jQuery.getJSON(preload_resource['original_url'])
        .done(
          function(data){
            self.showPreview(data);
          })
        .fail(
          function(jqxhr, textStatus, error) {
            jQuery.getJSON(preload_resource['url'])
            .done(
              function(data){
                self.showPreview(data);
              })
            .fail(
              function(jqXHR, textStatus, errorThrown) {
                self.showError(jqXHR, textStatus, errorThrown);
              }
            );
          }
        );
      } else {
        jQuery.getJSON(preload_resource['url']).done(
          function(data){
            self.showPreview(data);
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
        self.el.html(jqXHR.responseText);
      } else {
        self.el.html(self.i18n('error', {text: textStatus, error: errorThrown}));
      }
    },

    showPreview: function (geojsonFeature) {
      var self = this;
      var gjLayer = L.geoJson().addTo(self.map);
      gjLayer.addData(geojsonFeature);
      self.map.fitBounds(gjLayer.getBounds());
    }
  };
});
