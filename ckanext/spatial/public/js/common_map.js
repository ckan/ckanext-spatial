(function (ckan, jQuery) {

  /* Returns a Leaflet map to use on the different spatial widgets
   *
   * All Leaflet based maps should use this constructor to provide consistent
   * look and feel and avoid duplication.
   *
   * container        - HTML element or id of the map container
   * mapOptions       - (Optional) Options to pass to the map constructor
   * baseLayerOptions - (Optional) Options to pass to the base layer constructor 
   *
   * Examples
   *
   *   // Will return a map with attribution control
   *   var map = ckan.commonLeafletMap('map');
   *
   *   // For smaller maps where the attribution is shown outside the map, pass
   *   // the following option:
   *   var map = ckan.commonLeafletMap('map', {attributionControl: false});
   *
   * Returns a Leaflet map object.
   */
  ckan.commonLeafletMap = function (container, mapOptions, baseLayerOptions) {
      
      var mapOptions = mapOptions || {};
      var baseLayerOptions = jQuery.extend(baseLayerOptions, {
                maxZoom: 18,
                attribution: 'Map data &copy; OpenStreetMap contributors'
                });

      map = new L.Map(container, mapOptions);

      // MapQuest OpenStreetMap base map
      baseLayerUrl = '//otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png';
      baseLayerOptions.subdomains = '1234';
      baseLayerOptions.attribution += ', Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="//developer.mapquest.com/content/osm/mq_logo.png">';
      var baseLayer = new L.TileLayer(baseLayerUrl, baseLayerOptions);
      map.addLayer(baseLayer);

      return map;

  }

})(this.ckan, this.jQuery);
