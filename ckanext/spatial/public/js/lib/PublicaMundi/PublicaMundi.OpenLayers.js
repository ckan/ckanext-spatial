/// <reference path="PublicaMundi.js" />

(function (window, PublicaMundi) {
	"use strict";

	if (typeof PublicaMundi === 'undefined') {
		return;
	}
	
	PublicaMundi.define('PublicaMundi.OpenLayers');

	PublicaMundi.OpenLayers.Framework = 'OpenLayers';

	PublicaMundi.registerFrameworkResolver(PublicaMundi.OpenLayers.Framework, function () {
	    if ((PublicaMundi.isObject(ol)) && (PublicaMundi.isFunction(ol.Map))) {
	        return true;
	    }
	    return false;
	});


})(window, PublicaMundi);