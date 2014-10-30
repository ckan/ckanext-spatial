(function (window, PublicaMundi) {
	"use strict";

	if (typeof PublicaMundi === 'undefined') {
		return;
	}
	
	PublicaMundi.define('PublicaMundi.OpenLayers');

	PublicaMundi.OpenLayers.Framework = 'ol';

	PublicaMundi.registerFrameworkResolver(PublicaMundi.OpenLayers.Framework, function () {
	    if ((PublicaMundi.isObject(ol)) && (PublicaMundi.isFunction(ol.Map))) {
	        return true;
	    }
	    return false;
	});


})(window, PublicaMundi);