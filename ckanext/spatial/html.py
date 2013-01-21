SPATIAL_SEARCH_FORM_EXTRA_HEADER="""
    <link type="text/css" rel="stylesheet" media="all" href="/css/spatial_search_form.css" />
"""

SPATIAL_SEARCH_FORM_EXTRA_FOOTER="""
    <script type="text/javascript" src="js/openlayers/OpenLayers_dataset_map.js"></script>
    <script type="text/javascript" src="js/spatial_search_form.js"></script>
    <script type="text/javascript">
        //<![CDATA[
        $(document).ready(function(){
            CKAN.SpatialSearchForm.bbox = '%(bbox)s';
            CKAN.SpatialSearchForm.defaultExtent = '%(default_extent)s';
            CKAN.SpatialSearchForm.setup();
        })
        //]]>
    </script>
"""

SPATIAL_SEARCH_FORM="""
<input type="hidden" id="ext_bbox" name="ext_bbox" value="%(bbox)s" />
<input type="hidden" id="ext_prev_extent" name="ext_prev_extent" value="" />

<div id="spatial-search-show"><a href="#" class="more">Filter by location</a></div>
<div id="spatial-search-container">
    <div id="spatial-search-map-container">
        <div id="spatial-search-map" class="span3"></div>
        <div id="spatial-search-toolbar" class="span3">
            <input type="button" id="draw-box" value="Select an area" class="btn"/>
            <input type="button" id="clear-box" value="Clear" class="btn"/>
            <div class="helper">Click on the 'Select' button to draw an area of interest. Use the map controls or the mouse wheel to zoom. Drag to pan the map.</div>
        </div>
    </div>
    <div class="clearfix"></div>
    <div id="spatial-search-map-attribution">Map data CC-BY-SA by <a href="http://openstreetmap.org">OpenStreetMap</a> | Tiles by <a href="http://www.mapquest.com">MapQuest</a></div>
</div>
"""

MAP_ATTRIBUTION_OSM="""<div id="spatial-search-map-attribution">Map data CC-BY-SA by <a href="http://openstreetmap.org">OpenStreetMap</a> | Tiles by <a href="http://www.mapquest.com">MapQuest</a></div>"""
