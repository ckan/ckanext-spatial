<?xml version="1.0" encoding="utf-8"?>
<sch:schema xmlns:sch="http://www.ascc.net/xml/schematron">
<sch:pattern name="Bounding Coordinates Latitude Restriction">
	<sch:rule context="southbc">
		<sch:assert test=". &lt;= parent::bounding/northbc">South_Bounding_Coordinate (<sch:emph>southbc</sch:emph>) must be less than or equal to North_Bounding_Coordinate (<sch:emph>northbc</sch:emph>).</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="G-Ring Latitude Restriction">
	<sch:rule context="gringlat">
		<sch:assert test="(. &gt;= ancestor::spdom/bounding/southbc) and (. &lt;= ancestor::spdom/bounding/northbc)">G-Ring_Latitude (<sch:emph>gringlat</sch:emph>) must lie between the North_Bounding_Coordinate (<sch:emph>northbc</sch:emph>) and South_Bounding_Coordinate (<sch:emph>southbc</sch:emph>).</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="G-Ring Longitude Restrictions">
	<sch:rule context="gringlon[ancestor::spdom/bounding/westbc &lt;= ancestor::spdom/bounding/eastbc]">
		<sch:assert test="(. &gt;= ancestor::spdom/bounding/westbc) and (. &lt;= ancestor::spdom/bounding/eastbc)">G-Ring_Longitude (<sch:emph>gringlon</sch:emph>) must lie between the West_Bounding_Coordinate (<sch:emph>westbc</sch:emph>) and East_Bounding_Coordinate (<sch:emph>eastbc</sch:emph>).</sch:assert>
	</sch:rule>
	<sch:rule context="gringlon[ancestor::spdom/bounding/westbc &gt; ancestor::spdom/bounding/eastbc]">
		<sch:assert test="(. &gt;= ancestor::spdom/bounding/westbc) or (. &lt;= ancestor::spdom/bounding/eastbc)">G-Ring_Longitude (<sch:emph>gringlon</sch:emph>) must lie between the West_Bounding_Coordinate (<sch:emph>westbc</sch:emph>) and East_Bounding_Coordinate (<sch:emph>eastbc</sch:emph>).</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="G-Ring Restrictions">
	<sch:rule context="gring">
		<sch:assert test="( string-length(.) - string-length(translate(., ',', '')) ) mod 2 = 1">G-Ring (<sch:emph>gring</sch:emph>) does not contain an even number of values.</sch:assert>
		<sch:report test="( string-length(normalize-space(.)) - string-length(translate(normalize-space(.), '+-0123456789., ', '')) ) &gt; 0">G-Ring (<sch:emph>gring</sch:emph>) contains invalid characters.</sch:report>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Map Projection Restrictions">
	<sch:rule context="mapprojn[normalize-space(.) = 'Albers Conical Equal Area']">
		<sch:assert test="parent::mapproj/albers">Must use Albers_Conical_Equal_Area (<sch:emph>albers</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Albers Conical Equal Area".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Azimuthal Equidistant']">
		<sch:assert test="parent::mapproj/azimequi">Must use Azimuthal_Equidistant (<sch:emph>azimequi</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Azimuthal Equidistant".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Equidistant Conic']">
		<sch:assert test="parent::mapproj/equicon">Must use Equidistant_Conic (<sch:emph>equicon</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Equidistant Conic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Equirectangular']">
		<sch:assert test="parent::mapproj/equirect">Must use Equirectangular (<sch:emph>equirect</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Equirectangular".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'General Vertical Near-sided Perspective']">
		<sch:assert test="parent::mapproj/gvnsp">Must use General_Vertical_Near-sided_Perspective (<sch:emph>gvnsp</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "General Vertical Near-sided Perspective".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Gnomonic']">
		<sch:assert test="parent::mapproj/gnomonic">Must use Gnomonic (<sch:emph>gnomonic</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Gnomonic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Lambert Azimuthal Equal Area']">
		<sch:assert test="parent::mapproj/lamberta">Must use Lambert_Azimuthal_Equal_Area (<sch:emph>lamberta</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Lambert Azimuthal Equal Area".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Lambert Conformal Conic']">
		<sch:assert test="parent::mapproj/lambertc">Must use Lambert_Conformal_Conic (<sch:emph>lambertc</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Lambert Conformal Conic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Mercator']">
		<sch:assert test="parent::mapproj/mercator">Must use Mercator (<sch:emph>mercator</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Mercator".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Modified Stereographic for Alaska']">
		<sch:assert test="parent::mapproj/modsak">Must use Modified_Stereographic_for_Alaska (<sch:emph>modsak</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Modified Stereographic for Alaska".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Miller Cylindrical']">
		<sch:assert test="parent::mapproj/miller">Must use Miller_Cylindrical (<sch:emph>miller</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Miller Cylindrical".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Oblique Mercator']">
		<sch:assert test="parent::mapproj/obqmerc">Must use Oblique_Mercator (<sch:emph>obqmerc</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Oblique Mercator".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Orthographic']">
		<sch:assert test="parent::mapproj/orthogr">Must use Orthographic (<sch:emph>orthogr</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Orthographic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Polar Stereographic']">
		<sch:assert test="parent::mapproj/polarst">Must use Polar_Stereographic (<sch:emph>polarst</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Polar Stereographic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Polyconic']">
		<sch:assert test="parent::mapproj/polycon">Must use Polyconic (<sch:emph>polycon</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Polyconic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Robinson']">
		<sch:assert test="parent::mapproj/robinson">Must use Robinson (<sch:emph>robinson</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Robinson".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Sinusoidal']">
		<sch:assert test="parent::mapproj/sinusoid">Must use Sinusoidal (<sch:emph>sinusoid</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Sinusoidal".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Space Oblique Mercator (Landsat)']">
		<sch:assert test="parent::mapproj/spaceobq">Must use Space_Oblique_Mercator_(Landsat) (<sch:emph>spaceobq</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Space Oblique Mercator (Landsat)".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Stereographic']">
		<sch:assert test="parent::mapproj/stereo">Must use Stereographic (<sch:emph>stereo</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Stereographic".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'Transverse Mercator']">
		<sch:assert test="parent::mapproj/transmer">Must use Transverse_Mercator (<sch:emph>transmer</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "Transverse Mercator".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn[normalize-space(.) = 'van der Grinten']">
		<sch:assert test="parent::mapproj/vdgrin">Must use van_der_Grinten (<sch:emph>vdgrin</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is "van der Grinten".</sch:assert>
	</sch:rule>
	<sch:rule context="mapprojn">
		<sch:assert test="parent::mapproj/mapprojp">Must use Map_Projection_Parameters (<sch:emph>mapprojp</sch:emph>) if Map_Projection_Name (<sch:emph>mapprojn</sch:emph>) is not one of the 21 enumerated projection names.</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Landsat Number/Path Number Restrictions">
	<sch:rule context="pathnum[(parent::*/landsat &gt;= 1) and (parent::*/landsat &lt;= 3)]">
		<sch:assert test=". &lt; 251">Path_Number (<sch:emph>pathnum</sch:emph>) must be less than 251 for Landsats (<sch:emph>landsat</sch:emph>) 1, 2, or 3.</sch:assert>
	</sch:rule>
	<sch:rule context="pathnum[(parent::*/landsat = 4) or (parent::*/landsat = 5)]">
		<sch:assert test=". &lt; 233">Path_Number (<sch:emph>pathnum</sch:emph>) must be less than 233 for Landsats (<sch:emph>landsat</sch:emph>) 4 or 5.</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Grid Coordinate System Restrictions">
	<sch:rule context="gridsysn[normalize-space(.) = 'Universal Transverse Mercator']">
		<sch:assert test="parent::gridsys/utm">Must use Universal_Transverse_Mercator_(UTM) (<sch:emph>utm</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "Universal Transverse Mercator".</sch:assert>
	</sch:rule>
	<sch:rule context="gridsysn[normalize-space(.) = 'Universal Polar Stereographic']">
		<sch:assert test="parent::gridsys/ups">Must use Universal_Polar_Stereographic_(UPS) (<sch:emph>ups</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "Universal Polar Stereographic".</sch:assert>
	</sch:rule>
	<sch:rule context="gridsysn[normalize-space(.) = 'State Plane Coordinate System 1927']">
		<sch:assert test="parent::gridsys/spcs">Must use State_Plane_Coordinate_System_(SPCS) (<sch:emph>spcs</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "State Plane Coordinate System 1927".</sch:assert>
	</sch:rule>
	<sch:rule context="gridsysn[normalize-space(.) = 'State Plane Coordinate System 1983']">
		<sch:assert test="parent::gridsys/spcs">Must use State_Plane_Coordinate_System_(SPCS) (<sch:emph>spcs</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "State Plane Coordinate System 1983".</sch:assert>
	</sch:rule>
	<sch:rule context="gridsysn[normalize-space(.) = 'ARC Coordinate System']">
		<sch:assert test="parent::gridsys/arcsys">Must use ARC_Coordinate_System (<sch:emph>arcsys</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "ARC Coordinate System".</sch:assert>
	</sch:rule>
	<sch:rule context="gridsysn[normalize-space(.) = 'other grid system']">
		<sch:assert test="parent::gridsys/othergrd">Must use Other_Grid_System's_Definition (<sch:emph>othergrd</sch:emph>) if Grid_Coordinate_System_Name (<sch:emph>gridsysn</sch:emph>) is "other grid system".</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Planar Coordinate Information Restrictions">
	<sch:rule context="plance[normalize-space(.) = 'coordinate pair']">
		<sch:assert test="parent::planci/coordrep">Must use Coordinate_Representation (<sch:emph>coordrep</sch:emph>) if Planar_Coordinate_Encoding_Method (<sch:emph>plance</sch:emph>) is "coordinate pair".</sch:assert>
	</sch:rule>
	<sch:rule context="plance[normalize-space(.) = 'distance and bearing']">
		<sch:assert test="parent::planci/distbrep">Must use Distance_and_Bearing_Representation (<sch:emph>distbrep</sch:emph>) if Planar_Coordinate_Encoding_Method (<sch:emph>plance</sch:emph>) is "distance and bearing".</sch:assert>
	</sch:rule>
	<sch:rule context="plance[normalize-space(.) = 'row and column']">
		<sch:assert test="parent::planci/coordrep">Must use Coordinate_Representation (<sch:emph>coordrep</sch:emph>) if Planar_Coordinate_Encoding_Method (<sch:emph>plance</sch:emph>) is "row and column".</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Horizontal Datum Name/Ellipsoid Name Restrictions">
	<sch:rule context="horizdn[normalize-space(.) = 'North American Datum of 1927']">
		<sch:assert test="normalize-space(parent::geodetic/ellips) = 'Clarke 1866'">Ellipsoid_Name (<sch:emph>ellips</sch:emph>) must be "Clarke 1866" if Horizontal_Datum_Name (<sch:emph>horizdn</sch:emph>) is "North American Datum of 1927".</sch:assert>
	</sch:rule>
	<sch:rule context="horizdn[normalize-space(.) = 'North American Datum of 1983']">
		<sch:assert test="normalize-space(parent::geodetic/ellips) = 'Geodetic Reference System 80'">Ellipsoid_Name (<sch:emph>ellips</sch:emph>) must be "Geodetic Reference System 80" if Horizontal_Datum_Name (<sch:emph>horizdn</sch:emph>) is "North American Datum of 1983".</sch:assert>
	</sch:rule>
</sch:pattern>

<sch:pattern name="Bitrate Restriction">
	<sch:rule context="highbps">
		<sch:assert test=". &gt; parent::dialinst/lowbps">Highest BPS (<sch:emph>highbps</sch:emph>) must be greater than Lowest BPS (<sch:emph>lowbps</sch:emph>).</sch:assert>
	</sch:rule>
</sch:pattern>

</sch:schema>