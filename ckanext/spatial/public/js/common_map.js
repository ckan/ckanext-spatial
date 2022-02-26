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

          baseLayerUrl = '//{s}.tiles.mapbox.com/v4/' + mapConfig['mapbox.map_id'] + '/{z}/{x}/{y}.png?access_token=' + mapConfig['mapbox.access_token'];
          leafletBaseLayerOptions.handle = mapConfig['mapbox.map_id'];
          leafletBaseLayerOptions.subdomains = mapConfig.subdomains || 'abcd';
          leafletBaseLayerOptions.attribution = mapConfig.attribution || 'Data: <a href="http://osm.org/copyright" target="_blank">OpenStreetMap</a>, Design: <a href="http://mapbox.com/about/maps" target="_blank">MapBox</a>';

          baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions);

      } else if (mapConfig.type == 'custom') {
          // Custom XYZ layer
          baseLayerUrl = mapConfig['custom.url'];
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

      } else {
          // Default to Stamen base map
          baseLayerUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png';
          leafletBaseLayerOptions.subdomains = mapConfig.subdomains || 'abcd';
          leafletBaseLayerOptions.attribution = mapConfig.attribution || 'Map tiles by <a href="http://stamen.com">Stamen Design</a> (<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>). Data by <a href="http://openstreetmap.org">OpenStreetMap</a> (<a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>)';

          baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions);
      }

      map.addLayer(baseLayer);

      function getColor(i) {
          pallet = ["#1f78b4","#e31a1c","#fb9a99","#fdbf6f","#ff7f00","#cab2d6","#6a3d9a","#ffff99","#a6cee3","#b2df8a","#33a02c"];
          if(i>10){
            return '#FFEDA0';
          }
          return pallet[i];
      }

      function myStyle(i) {
        return {
          "color": getColor(i),
          "weight": 2,
          "opacity": 1,
          "fillColor": getColor(i),
          "fillOpacity": 0.1,
          "clickable": false
        };
      }

      let urls = []
      if (mapConfig.geoJsonLayerURLs) {
        urls = JSON.parse(mapConfig.geoJsonLayerURLs);
        var GJLayers = L.layerGroup().addTo(map)
        for(const [i, url] of urls.entries()){
          fetch(
            url
          ).then(
            res => res.json()
          ).then(
            data => GJLayers.addLayer(
              L.geoJSON(
                data,
                {
                  style: myStyle(i),
                  onEachFeature: function (feature, layer) {
                    if(feature.properties && feature.properties.name){
                      layer.bindPopup(feature.properties.name);
                    }
                  }
                }
              )
            )            
          )
        }
      }
      return map;
  }

})(this.ckan, this.jQuery);
