/* Copyright (c) 2006-2010 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the Clear BSD license.  
 * See http://svn.openlayers.org/trunk/openlayers/license.txt for the
 * full text of the license. */

/**
 * @requires OpenLayers/Format/GeoJSON.js
 * @requires OpenLayers/Format/JSON.js
 * @requires OpenLayers/Feature/Vector.js
 * @requires OpenLayers/Geometry/Point.js
 * @requires OpenLayers/Geometry/MultiPoint.js
 * @requires OpenLayers/Geometry/LineString.js
 * @requires OpenLayers/Geometry/MultiLineString.js
 * @requires OpenLayers/Geometry/Polygon.js
 * @requires OpenLayers/Geometry/MultiPolygon.js
 * @requires OpenLayers/Console.js
 */

/**
 * Class: OpenLayers.Format.EsriGeoJSON
 * Read and (write) EsriGeoJSON. Create a new parser with the
 *     <OpenLayers.Format.EsriGeoJSON> constructor.
 *
 * Inherits from:
 *  - <OpenLayers.Format.GeoJSON>
 */
OpenLayers.Format.EsriGeoJSON = OpenLayers.Class(OpenLayers.Format.GeoJSON, {

    /**
     * Constructor: OpenLayers.Format.EsriGeoJSON
     * Create a new parser for EsriGeoJSON.
     *
     * Parameters:
     * options - {Object} An optional object whose properties will be set on
     *     this instance.
     */
    initialize: function(options) {
        OpenLayers.Format.GeoJSON.prototype.initialize.apply(this, [options]);
    },

    /**
     * APIMethod: read
     * Deserialize a EsriGeoJSON string.
     *
     * Parameters:
     * json - {String} A EsriGeoJSON string
     * Returns: 
     * {Object} an array of <OpenLayers.Feature.Vector>
     */
    read: function(json) {
        var results = null;
        var obj = null;
        if (typeof json == "string") {
            obj = OpenLayers.Format.JSON.prototype.read.apply(this,
                                                              [json]);
        } else { 
            obj = json;
        }    
        if(!obj) {
            OpenLayers.Console.error("Bad JSON: " + json);
        } else{
            results = this.parseEsriGeoJSON2OL(obj);
        }
        return results;
    },
    
    parseEsriGeoJSON2OL: function (esri_geojson) {//parse Esri GeoJSON to the OpenLayers GeoJSON
		var geom_type = esri_geojson.geometryType;
		var epsg_code = esri_geojson.spatialReference.wkid;

		var result_feats = [];
		if(geom_type === 'esriGeometryPolygon') {
			for (var i=0; i < esri_geojson.features.length; i++) 
			{
				var feat = esri_geojson.features[i];
				var feature_property = '{';
				for(var prop in feat.attributes) {
					feature_property += '"' + prop + '":"' + feat.attributes[prop] + '",';
				}
				if(feature_property.length > 1) {
					feature_property = feature_property.substring(0, feature_property.length - 1);
				}
				feature_property += '}';
				
				//get the geometry
				var o = feat.geometry;
				//loop through all the rings
				var ring_count = o.rings.length;
				if(ring_count === 1) {
					//create geojson start & end - i know i'm getting polygons	        
					var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"Polygon", "coordinates":[['	                
					var geojsonend = ']]}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';

					//the coordinates for this ring
					var coords = o.rings[0];
					
					//loop through each coordinate
					var coordPair="";
					for (var g=0; g < coords.length; g++) 
					{
						if(g==coords.length-1){
							coordPair = coordPair+"["+coords[g]+"]";
						}else{
							coordPair=coordPair+"["+coords[g]+"],";
						}
					}

					//combine to create geojson string
					var new_ol_feats = this.esriDeserialize(geojsonstart+coordPair+geojsonend);
					if(new_ol_feats) {
						result_feats = result_feats.concat(new_ol_feats);
					}
				} else if (ring_count > 1) {
					//create geojson start & end - i know i'm getting polygons	        
					var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"MultiPolygon", "coordinates":[['	                
					var geojsonend = ']]}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';
					
					var total_coords = "";
					for (var s=0; s < ring_count; s++) 
					{
						//the coordinates for this ring
						var coords = o.rings[s];
						
						//loop through each coordinate
						var coordPair="[";
						for (var g=0; g < coords.length; g++) 
						{
							if(g==coords.length-1){
								coordPair = coordPair+"["+coords[g]+"]";
							}else{
								coordPair=coordPair+"["+coords[g]+"],";
							}
						}
						
						if(s === ring_count - 1) {
							coordPair += "]";
						} else {
							coordPair += "],";
						}
						
						total_coords += coordPair;
					}
					
					//combine to create geojson string
					var new_ol_feats = this.esriDeserialize(geojsonstart+total_coords+geojsonend);
					if(new_ol_feats) {
						result_feats = result_feats.concat(new_ol_feats);
					}
				}
			}
		} else if (geom_type === 'esriGeometryPolyline') {
			for (var i=0; i < esri_geojson.features.length; i++) 
			{
				var feat = esri_geojson.features[i];
				var feature_property = '{';
				for(var prop in feat.attributes) {
					feature_property += '"' + prop + '":"' + feat.attributes[prop] + '",';
				}
				if(feature_property.length > 1) {
					feature_property = feature_property.substring(0, feature_property.length - 1);
				}
				feature_property += '}';
				
				//get the geometry
				var o = feat.geometry;
				var path_count = o.paths.length;
				if(path_count === 1) { //LineString
					var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"LineString", "coordinates":['	                
					var geojsonend = ']}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';
					
					var coords = o.paths[0];
					var coordPair="";
					for (var g=0; g < coords.length; g++) 
					{
						if(g==coords.length-1){
							coordPair = coordPair+"["+coords[g]+"]";
						}else{
							coordPair=coordPair+"["+coords[g]+"],";
						}
					}
					
					//combine to create geojson string
					var new_ol_feats = this.esriDeserialize(geojsonstart+coordPair+geojsonend);
					if(new_ol_feats) {
						result_feats = result_feats.concat(new_ol_feats);
					}
				} else if (path_count > 1) { //MultiLineString
					var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"MultiLineString", "coordinates":['	                
					var geojsonend = ']}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';
					
					//loop through all the rings
					var total_coords = "";
					for (var s=0; s < path_count; s++) 
					{
						//the coordinates for this ring
						var coords = o.paths[s];
						
						//loop through each coordinate
						var coordPair="[";
						for (var g=0; g < coords.length; g++) 
						{
							if(g==coords.length-1){
								coordPair = coordPair+"["+coords[g]+"]";
							}else{
								coordPair=coordPair+"["+coords[g]+"],";
							}
						}
						
						if(s === path_count - 1) {
							coordPair += "]";
						} else {
							coordPair += "],";
						}
						
						total_coords += coordPair;
					}
					
					//combine to create geojson string
					var new_ol_feats = this.esriDeserialize(geojsonstart+total_coords+geojsonend);
					if(new_ol_feats) {
						result_feats = result_feats.concat(new_ol_feats);
					}
				}
				
			}
		} else if (geom_type === 'esriGeometryMultipoint') {
			for (var i=0; i < esri_geojson.features.length; i++) 
			{
				var feat = esri_geojson.features[i];
				var feature_property = '{';
				for(var prop in feat.attributes) {
					feature_property += '"' + prop + '":"' + feat.attributes[prop] + '",';
				}
				if(feature_property.length > 1) {
					feature_property = feature_property.substring(0, feature_property.length - 1);
				}
				feature_property += '}';
				
				//get the geometry
				var o = feat.geometry;
				var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"MultiPoint", "coordinates":['	                
				var geojsonend = ']}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';
				
				//loop through all the rings
				var total_coords = "";
				for (var s=0; s < o.length; s++) 
				{
					//the coordinates for this ring
					var coords = o[s];
					
					//loop through each coordinate
					var coordPair="[" + coords.x + "," + coords.y;
					
					if(s === path_count - 1) {
						coordPair += "]";
					} else {
						coordPair += "],";
					}
					
					total_coords += coordPair;
				}
				
				//combine to create geojson string
				var new_ol_feats = this.esriDeserialize(geojsonstart+total_coords+geojsonend);
				if(new_ol_feats) {
					result_feats = result_feats.concat(new_ol_feats);
				}
			}
		} else if (geom_type === 'esriGeometryPoint') {
			for (var i=0; i < esri_geojson.features.length; i++) 
			{
				var feat = esri_geojson.features[i];
				var feature_property = '{';
				for(var prop in feat.attributes) {
					feature_property += '"' + prop + '":"' + feat.attributes[prop] + '",';
				}
				if(feature_property.length > 1) {
					feature_property = feature_property.substring(0, feature_property.length - 1);
				}
				feature_property += '}';
				
				//get the geometry
				var o = feat.geometry;
				var geojsonstart = '{"type":"Feature", "properties":' + feature_property + ', "geometry":{"type":"Point", "coordinates":['	                
				var geojsonend = ']}, "crs":{"type":"EPSG", "properties":{"code":' + epsg_code + '}}}';
				var coordPair = o.x + "," + o.y;
				//combine to create geojson string
				var new_ol_feats = this.esriDeserialize(geojsonstart+coordPair+geojsonend);
				if(new_ol_feats) {
					result_feats = result_feats.concat(new_ol_feats);
				}
			}
		}
		
		if(result_feats.length > 0) {
			return result_feats;
		} else {
			return null;
		}
	},
	
	esriDeserialize: function (geojson) {
		var features = OpenLayers.Format.GeoJSON.prototype.read.apply(this,
                                                              [geojson]);
		if(features) 
		{
			if(features.constructor != Array) {
				features = [features];
			}
			
			return features;
		} else {
			return null;
		}
	},

    /**
     * APIMethod: write
     * Serialize a feature, geometry, array of features into a GeoJSON string.
     *
     * Parameters:
     * obj - {Object} An <OpenLayers.Feature.Vector>, <OpenLayers.Geometry>,
     *     or an array of features.
     * pretty - {Boolean} Structure the output with newlines and indentation.
     *     Default is false.
     *
     * Returns:
     * {String} The GeoJSON string representation of the input geometry,
     *     features, or array of features.
     */
    write: function(obj, pretty) {
        var geojson = {
            "type": null
        };
        if(obj instanceof Array) {
            geojson.type = "FeatureCollection";
            var numFeatures = obj.length;
            geojson.features = new Array(numFeatures);
            for(var i=0; i<numFeatures; ++i) {
                var element = obj[i];
                if(!element instanceof OpenLayers.Feature.Vector) {
                    var msg = "FeatureCollection only supports collections " +
                              "of features: " + element;
                    throw msg;
                }
                geojson.features[i] = this.extract.feature.apply(
                    this, [element]
                );
            }
        } else if (obj.CLASS_NAME.indexOf("OpenLayers.Geometry") == 0) {
            geojson = this.extract.geometry.apply(this, [obj]);
        } else if (obj instanceof OpenLayers.Feature.Vector) {
            geojson = this.extract.feature.apply(this, [obj]);
            if(obj.layer && obj.layer.projection) {
                geojson.crs = this.createCRSObject(obj);
            }
        }
        return OpenLayers.Format.JSON.prototype.write.apply(this,
                                                            [geojson, pretty]);
    },

    CLASS_NAME: "OpenLayers.Format.EsriGeoJSON" 

});     
