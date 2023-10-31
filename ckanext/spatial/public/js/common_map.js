(function (ckan, jQuery) {

  /* Returns a Leaflet map to use on the different spatial widgets
   *
   * All Leaflet based maps should use this constructor to provide consistent
   * look and feel and avoid duplication.
   *
   * container               - HTML element or id of the map container
   * mapConfig               - (Optional) CKAN config related to the base map.
   *                           These are defined in the config ini file (eg
   *                           map type, API keys if necessary, etc).
   * leafletMapOptions       - (Optional) Options to pass to the Leaflet Map constructor
   * leafletBaseLayerOptions - (Optional) Options to pass to the Leaflet TileLayer constructor
   *
   * Examples
   *
   *   // Will return a map with attribution control
   *   var map = ckan.commonLeafletMap('map', mapConfig);
   *
   *   // For smaller maps where the attribution is shown outside the map, pass
   *   // the following option:
   *   var map = ckan.commonLeafletMap('map', mapConfig, {attributionControl: false});
   *
   * Returns a Leaflet map object.
   */
  ckan.commonLeafletMap = function (container,
                                    mapConfig,
                                    leafletMapOptions,
                                    leafletBaseLayerOptions) {

      var isHttps = window.location.href.substring(0, 5).toLowerCase() === 'https';
      var mapConfig = mapConfig || {type: 'stamen'};
      var leafletMapOptions = leafletMapOptions || {};
      var leafletBaseLayerOptions = jQuery.extend(leafletBaseLayerOptions, {
                maxZoom: 18
                });

      var baseLayer;

      map = new L.Map(container, leafletMapOptions);

      if (mapConfig.type == 'mapbox') {
          // MapBox base map
          if (!mapConfig['mapbox.map_id'] || !mapConfig['mapbox.access_token']) {
            throw '[CKAN Map Widgets] You need to provide a map ID ([account].[handle]) and an access token when using a MapBox layer. ' +
                  'See http://www.mapbox.com/developers/api-overview/ for details';
          }

          baseLayer = L.tileLayer.provider('MapBox', {
                id: mapConfig['mapbox.map_id'],
                accessToken: mapConfig['mapbox.access_token']
          });

      } else if (mapConfig.type == 'custom') {
          // Custom XYZ layer
          baseLayerUrl = mapConfig['custom_url'] || mapConfig['custom.url'];
          if (mapConfig.subdomains) leafletBaseLayerOptions.subdomains = mapConfig.subdomains;
          if (mapConfig.tms) leafletBaseLayerOptions.tms = mapConfig.tms;
          leafletBaseLayerOptions.attribution = mapConfig.attribution;

          baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions);

      } else if (mapConfig.type == 'wms') {

          baseLayerUrl = mapConfig['wms.url'];
          wmsOptions = {}
          wmsOptions['layers'] = mapConfig['wms.layers'];
          wmsOptions['styles'] = mapConfig['wms.styles'] || '';
          wmsOptions['format'] = mapConfig['wms.format'] || 'image/png';
          if(mapConfig['wms.srs'] || mapConfig['wms.crs']) {
              wmsOptions['crs'] = mapConfig['wms.srs'] || mapConfig['wms.crs'];
          }
          wmsOptions['version'] = mapConfig['wms.version'] || '1.1.1';

          baseLayer = new L.TileLayer.WMS(baseLayerUrl, wmsOptions);


      } else if (mapConfig.type) {

        baseLayer = L.tileLayer.provider(mapConfig.type, mapConfig)

      } else {
        let c = L.Control.extend({

          onAdd: (map) => {
            let element = document.createElement("div");
            element.className = "leaflet-control-no-provider";
            element.innerHTML = 'No map provider set. Please check the <a href="https://docs.ckan.org/projects/ckanext-spatial/en/latest/map-widgets.html">documentation</a>';
            return element;
          },
          onRemove: (map) => {}
        })
        map.addControl(new c({position: "bottomleft"}))

      }

      if (baseLayer) {
        let attribution = L.control.attribution({"prefix": false});
        attribution.addTo(map)

        map.addLayer(baseLayer);

        if (mapConfig.attribution) {
          attribution.addAttribution(mapConfig.attribution);
        }
      }

      return map;

  }

})(this.ckan, this.jQuery);
