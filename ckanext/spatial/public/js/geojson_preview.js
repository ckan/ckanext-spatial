// geojson preview module
ckan.module('geojsonpreview', function (jQuery, _) {
  return {
    options: {
      table: '<table class="table table-striped table-bordered table-condensed"><tbody>{body}</tbody></table>',
      row:'<tr><th>{key}</th><td>{value}</td></tr>',
      style: {
        opacity: 0.7,
        fillOpacity: 0.1,
        weight: 2
      },
      i18n: {
        'error': _('An error occurred: %(text)s %(error)s')
      }
    },
    initialize: function () {
      var self = this;

      self.el.empty();
      self.el.append($("<div></div>").attr("id","map"));
      self.map = ckan.commonLeafletMap('map', this.options.map_config);

      // hack to make leaflet use a particular location to look for images
      L.Icon.Default.imagePath = this.options.site_url + 'js/vendor/leaflet/images';


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
        this.el.html(jqXHR.responseText);
      } else {
        this.el.html(this.i18n('error', {text: textStatus, error: errorThrown}));
      }
    },

    showPreview: function (geojsonFeature) {
      var self = this;
      var gjLayer = L.geoJson(geojsonFeature, {
        style: self.options.style,
        onEachFeature: function(feature, layer) {
          var body = '';
          jQuery.each(feature.properties, function(key, value){
            if (value != null && typeof value === 'object') {
              value = JSON.stringify(value);
            }
            body += L.Util.template(self.options.row, {key: key, value: value});
          });
          var popupContent = L.Util.template(self.options.table, {body: body});
          layer.bindPopup(popupContent);
        }
      }).addTo(self.map);
      self.map.fitBounds(gjLayer.getBounds());
    }
  };
});
