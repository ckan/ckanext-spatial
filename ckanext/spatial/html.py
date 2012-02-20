MAP_VIEW="""
<div class="mapview">
    <a href="/dataset/%(name)s/map">View available WMS layers &raquo;</a>
</div>
"""

PACKAGE_MAP="""
<hr class="cleared" />
<div class="dataset-map subsection">
<h3>%(title)s</h3>
<div id="dataset-map-container"></div>
<div id="dataset-map-attribution">Map data CC-BY-SA by <a href="http://openstreetmap.org">OpenStreetMap</a> | Tiles courtesy of <a href="http://www.mapquest.com">MapQuest</a></div>
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

SPATIAL_SEARCH_FORM_EXTRA_HEADER="""
    <link type="text/css" rel="stylesheet" media="all" href="/ckanext/spatial/css/spatial_search_form.css" />
"""

SPATIAL_SEARCH_FORM_EXTRA_FOOTER="""
    <script type="text/javascript" src="/ckanext/spatial/js/openlayers/OpenLayers_dataset_map.js"></script>
    <script type="text/javascript" src="/ckanext/spatial/js/spatial_search_form.js"></script>
    <script type="text/javascript">
        //<![CDATA[
        $(document).ready(function(){
            CKAN.SpatialSearchForm.bbox = '%(bbox)s';
            CKAN.SpatialSearchForm.setup();
        })
        //]]>
    </script>
"""

SPATIAL_SEARCH_FORM="""
<input type="hidden" id="ext_bbox" name="ext_bbox" value="%(bbox)s" />
<div id="spatial-search-show"><a href="#" class="more">Filter by location</a></div>
<div id="spatial-search-container">
    <div id="spatial-search-map-container">
        <div id="spatial-search-map"></div>
        <div id="spatial-search-toolbar">
            <input type="button" id="draw-box" value="Select an area" class="pretty-button"/>
            <input type="button" id="clear-box" value="Clear" class="pretty-button"/>
            <div class="helper">Click on the 'Select' button to draw an area of interest. Use the map controls or the mouse wheel to zoom. Drag to pan the map.</div>
        </div>
    </div>
    <div id="spatial-search-map-attribution">Map data CC-BY-SA by <a href="http://openstreetmap.org">OpenStreetMap</a> | Tiles by <a href="http://www.mapquest.com">MapQuest</a></div>
</div>
"""
