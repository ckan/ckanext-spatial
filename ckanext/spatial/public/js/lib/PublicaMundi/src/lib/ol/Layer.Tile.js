(function (global, PublicaMundi, ol) {
    if (typeof PublicaMundi === 'undefined') {
        return;
    }

    if (typeof ol === 'undefined') {
        return;
    }

    PublicaMundi.define('PublicaMundi.OpenLayers.Layer');

    PublicaMundi.OpenLayers.Layer.Tile = PublicaMundi.Class(PublicaMundi.Layer, {
        initialize: function (options) {
            PublicaMundi.Layer.prototype.initialize.call(this, options);

            this._layer = new ol.layer.Tile({
                title: options.title,
                type: 'base', 
                source: new ol.source.XYZ({
                    url: options.url
                })
            });
            var urls = [];
            if (options.url.indexOf('{s}') < 0) {
                urls.push(options.url);
            } else {
                var subdomains = options.subdomains || 'abc';

                if (!PublicaMundi.isArray(subdomains)) {
                    subdomains = subdomains.split('');
                }
                for (var index = 0; index < subdomains.length; index++) {
                    urls.push(options.url.replace('{s}', subdomains[index]));
                }
            }
            this._layer.getSource().setUrls(urls);
        }
    });

    PublicaMundi.registry.registerLayerType({
        layer: PublicaMundi.LayerType.TILE,
        framework: PublicaMundi.OpenLayers.Framework,
        type: 'PublicaMundi.Layer.Tile',
        factory: PublicaMundi.OpenLayers.Layer.Tile
    });
})(window, window.PublicaMundi, ol);
