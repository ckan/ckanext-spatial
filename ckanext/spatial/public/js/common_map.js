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
      } else if (mapConfig.type == 'custom') {
          // Custom XYZ layer
          baseLayerUrl = mapConfig['custom.url'];
          if (mapConfig.subdomains) leafletBaseLayerOptions.subdomains = mapConfig.subdomains;
          if (mapConfig.tms) leafletBaseLayerOptions.tms = mapConfig.tms;
          leafletBaseLayerOptions.attribution = mapConfig.attribution;
     // Custom multi-layer map
     } else if (mapConfig.type === 'multilayer') {   
	// parse layer-specific mapConfig properties into array of layers
	mapConfig.layerprops = (function (mc) {
	  var match = [];
	  var ma;
	  for (var mprop in mc) {
	    if ((ma = /^(layer_)(\d+)\.(.+)$/.exec(mprop))) {
	      match.push(ma);
	    }
	  }
	  return(match);
	})(mapConfig);
	// construct a sorted list of layernames
	mapConfig.layerlist = (function (mc) {
	  var ll = [];
	  var layername;
	  var anum;
	  var bnum;
	  // get layer-number from layername
	  function tonum(s) {
	    return(parseInt(/^layer_(\d+)$/i.exec(s)[1]));
	  };
	  // build list of layernames
	  for (var i = 0; i < mc.layerprops.length; i++) {
	    layername = mc.layerprops[i][1] + mc.layerprops[i][2];
	    if (ll.indexOf(layername) === -1) {
	      ll.push(layername);
	    }
	  }
	  // sort layerlist
	  ll = ll.sort(function (a, b) {
	    return(tonum(a) - tonum(b));
	  });
	  return(ll);
	})(mapConfig);
	// update mapConfig to contain strucutred layer-properties
	mapConfig = (function (mc) {
	  var l;
	  var newkey;
	  for (var i = 0; i < mc.layerprops.length; i++) {
	    l = mc.layerprops[i];
	    newkey = l[1] + l[2]; 
	    mc[newkey] = mc[newkey] || {};
	    mc[newkey][l[3]] = mc[l[0]];
	    delete mc[l[0]];
	  }
	  delete mc.layerprops;
	  return(mc);
	})(mapConfig);
      } else {
          // Default to Stamen base map
          baseLayerUrl = 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png';
          leafletBaseLayerOptions.subdomains = mapConfig.subdomains || 'abcd';
          leafletBaseLayerOptions.attribution = mapConfig.attribution || 'Map tiles by <a href="http://stamen.com">Stamen Design</a> (<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>). Data by <a href="http://openstreetmap.org">OpenStreetMap</a> (<a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>)';
      }

     if (mapConfig.type === 'multilayer') {
       mapConfig.layerlist.forEach(function (lname) {
	 var url = mapConfig[lname].url;
	 var options = {};
	 // extract layeroptions
	 delete mapConfig[lname].url;
	 for (var prop in mapConfig[lname]) {
	   if (mapConfig[lname].hasOwnProperty(prop)) {
	     options[prop] = mapConfig[lname][prop];
	   }
	 }
     	 map.addLayer(new L.TileLayer(url, options));
       });
     } else {
       var baseLayer = new L.TileLayer(baseLayerUrl, leafletBaseLayerOptions);
       map.addLayer(baseLayer);
     }
     return map;
  };
})(this.ckan, this.jQuery);
