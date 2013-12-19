
// WMS preview module
this.ckan.module('wmspreview', function (jQuery, _) {

    // Private
    var defaultVersion = "1.1.1";

    var preferredFormat = "image/png";

    var proxy = false;

    var getParameterByName = function(name,query_string) {
      query_string = query_string || window.location.search;
      var match = RegExp('[?&]' + name + '=([^&]*)')
                    .exec(query_string);
      return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
    }

    var cleanUrl = function(server){
      var qs;
      if (server.indexOf("?") !== -1){
        parts = server.split("?");
        server = parts[0];
        qs = parts[1];
      }

      var mapParam = getParameterByName("map", "?" + qs);
      if (mapParam)
        server = server + "?map=" + mapParam;

      return server;
    }

    var getCapabilitiesUrl = function(server,version){

        version = version || defaultVersion;

        if (server.indexOf("?") === -1)
            server += "?"
        if (server.indexOf("=") !== -1)
            server += "&"

        var url  = server +
                   "SERVICE=WMS" +
                   "&REQUEST=GetCapabilities" +
                   "&VERSION=" + version;

        return (proxy) ? proxy + escape(url) : url;
    }

    var getFormat = function(formats){
      for(var i = 0; i < formats.length; i++){
        if (formats[i] == preferredFormat){
          return formats[i];
        }
      }
      return formats[0];
    }
  
  return {
    options: {
      i18n: {
      }
    },

    initialize: function () {
      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function() {

        var server = preload_resource.url;
        var wmsUrl = cleanUrl(server);
        var proxied_server = preload_resource.proxy_url;
        var capabilitiesUrl = getCapabilitiesUrl(proxied_server);

        var self = this;
        $.get(capabilitiesUrl,function(data){
          // Most WMS Servers will return the version they prefer,
          // regardless of which one you requested, so better check
          // for the actual version returned.
          var version = $(data).find("WMS_Capabilities").attr("version"); // 1.3.0
          if (!version)
              version = $(data).find("WMS_MS_Capabilities").attr("version"); // 1.1.1

          var format = new OpenLayers.Format.WMSCapabilities({"version":version});

          var capabilities = format.read(data);
          
          if (!capabilities.capability){
            $("#main").prepend(
              $("<div></div>").attr("class","flash-banner-box").append(
                $("<div></div>").attr("class","flash-banner error").html(
                  "Error parsing the WMS capabilities document")));
            return false;
          }


          var layers = capabilities.capability.layers;

          var olLayers = [];
          var maxExtent = false;
          var maxScale = false;
          var minScale = false;
          for (var count = 0; count < layers.length; count++){
            layer = layers[count];

            // Extend the maps's maxExtent to include this layer extent
            layerMaxExtent = new OpenLayers.Bounds(layer.llbbox[0],layer.llbbox[1],layer.llbbox[2],layer.llbbox[3]);
            if (!maxExtent){
                maxExtent = layerMaxExtent;
            } else {
                maxExtent.extend(layerMaxExtent);
            }
            if (layer.maxScale && (layer.maxScale > maxScale || maxScale === false)) maxScale = layer.maxScale;
            if (layer.minScale && (layer.minScale < minScale || minScale === false)) minScale = layer.minScale;
            olLayers.push(new OpenLayers.Layer.WMS(
              layer.title,
              wmsUrl,
              {"layers": layer.name,
              "format": getFormat(layer.formats),
              "transparent":true
              },
              {"buffer":0,
              "maxExtent": layerMaxExtent,
              "maxScale": (layer.maxScale) ? layer.maxScale : null,
              "minScale": (layer.minScale) ? layer.minScale : null,
              "isBaseLayer": false,
              "visibility": (count == 0)
              })  //Tiled?
            );

          }

          var dummyLayer = new OpenLayers.Layer("Dummy",{
            "maxExtent": maxExtent,
            "displayInLayerSwitcher":true,
            "isBaseLayer":true,
            "visibility":false,
            "minScale": (minScale) ? minScale : null,
            "maxScale": (maxScale) ? maxScale : null
          });
//          olLayers.push(dummyLayer);

var cloudmade_url = '.cloudmade.com/98a0ce317ad942cea786ded25271f410/116858/256/${z}/${x}/${y}.png';
if (window.location.protocol != "https:") {
var base_urls = ['http://a.tiles'+cloudmade_url,'http://b.tiles'+cloudmade_url,'http://c.tiles'+cloudmade_url];
} else {
var base_urls = ['https://ssl_tiles'+cloudmade_url];
        }          

          var baseLayer = new OpenLayers.Layer.OSM("OSM",base_urls,{
tileOptions: {crossOriginKeyword: null}
          });
 olLayers.push(baseLayer);
          $("#data-preview").empty();
          $("#data-preview").append($("<div></div>").attr("id","map"));
    var geographic = new OpenLayers.Projection("EPSG:4326");
    var mercator = new OpenLayers.Projection("EPSG:900913");
          // Create a new map
          self.map = new OpenLayers.Map("map" ,
            {
              "projection": mercator,
              "maxResolution":"auto",
              "controls":[
                  new OpenLayers.Control.PanZoomBar(),
                  new OpenLayers.Control.Navigation(),
                  new OpenLayers.Control.CustomMousePosition({
                      "displayClass":"olControlMousePosition",
                      "numDigits":4
                  }),
                  new OpenLayers.Control.LayerSwitcher({
                      "div": document.getElementById("layers"),
                      "roundedCorner":false
                  })
              ],
              "theme":"/js/vendor/openlayers/theme/default/style.css"
            });

          self.map.maxExtent = maxExtent.transform(geographic,mercator);
          self.map.addLayers(olLayers);
info = new OpenLayers.Control.WMSGetFeatureInfo({
            url: wmsUrl, 
            title: 'Identify features by clicking',
            queryVisible: true,
            eventListeners: {
                getfeatureinfo: function(event) {
                    self.map.addPopup(new OpenLayers.Popup.FramedCloud(
                        "info", 
                        self.map.getLonLatFromPixel(event.xy),
                        null,
                        event.text,
                        null,
                        true
                    ));
                }
            }
        });
        self.map.addControl(info);
        info.activate();

          self.map.zoomTo(11);
      });
    }
  }
});

OpenLayers.ImgPath = "/js/vendor/openlayers/img/";

OpenLayers.Control.CustomMousePosition = OpenLayers.Class(OpenLayers.Control.MousePosition,{
  formatOutput: function(lonLat) {
      var newHtml =  OpenLayers.Control.MousePosition.prototype.formatOutput.apply(this, [lonLat]);
      newHtml = "1:" + parseInt(this.map.getScale()) + " |  WGS84 " + newHtml;
      return newHtml;
  },

  CLASS_NAME: "OpenLayers.Control.CustomMousePosition"
});
