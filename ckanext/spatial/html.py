MAP_VIEW="""
<div class="mapview">
    <a href="/package/%(name)s/map">View available WMS layers &raquo;</a>
</div>
"""

PACKAGE_MAP="""
<hr class="cleared" />
<div class="dataset-map subsection">
<h3>%(title)s</h3>
<div id="dataset-map-container"></div>
</div>
"""

PACKAGE_MAP_EXTRA_HEADER="""
    <link type="text/css" rel="stylesheet" media="all" href="/ckanext/spatial/css/dataset_map.css" />
"""

PACKAGE_MAP_EXTRA_FOOTER="""
    <script type="text/javascript" src="/ckanext/spatial/js/openlayers/OpenLayers_dataset_map.js"></script>
    <script type="text/javascript" src="/ckanext/spatial/js/dataset_map.js"></script>
    <script type="text/javascript">
        //<![CDATA[
        $(document).ready(function(){
            CKAN.DatasetMap.extent = '%(extent)s';
            CKAN.DatasetMap.setup();
        })
        //]]>
    </script>


"""
