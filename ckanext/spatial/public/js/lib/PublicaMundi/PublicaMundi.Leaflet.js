/// <reference path="PublicaMundi.js" />

(function (window, PublicaMundi) {
	"use strict";

	if (typeof PublicaMundi === 'undefined') {
		return;
	}

	PublicaMundi.define('PublicaMundi.Leaflet');

	PublicaMundi.Leaflet.Framework = 'Leaflet';

	PublicaMundi.registerFrameworkResolver(PublicaMundi.Leaflet.Framework, function () {
	    if ((PublicaMundi.isObject(L)) && (PublicaMundi.isFunction(L.Map))) {
	        return true;
	    }
	    return false;
	});

})(window, PublicaMundi);