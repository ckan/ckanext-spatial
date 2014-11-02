module.exports = function (grunt) {
    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            options: {
                reporter: require('jshint-stylish')
            },
            publicamundi: ['src/*.js'],
            openlayers: ['src/lib/ol/*.js'],
            leaflet: ['src/lib/leaflet/*.js']
        },
        concat: {
            options: {
                banner: '/* <%= pkg.description %> version <%= pkg.version %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
                separator: ';',
                sourceMap: true
            },
            publicamundi: {
                src: ['src/PublicaMundi.js',
                      'src/Map.js',
                      'src/Layer.js'],
                dest: 'build/publicamundi-src.js'
            },
            openlayers: {
                src: ['src/lib/ol/PublicaMundi.OpenLayers.js',
                      'src/lib/ol/Map.js',
                      'src/lib/ol/Layer.WMS.js',
                      'src/lib/ol/Layer.Tile.js',
                      'src/lib/ol/Layer.GeoJson.js'],
                dest: 'build/publicamundi.ol-src.js'
            },
            leaflet: {
                src: ['src/lib/leaflet/PublicaMundi.Leaflet.js',
                      'src/lib/leaflet/Map.js',
                      'src/lib/leaflet/Layer.WMS.js',
                      'src/lib/leaflet/Layer.Tile.js',
                      'src/lib/leaflet/Layer.GeoJson.js'],
                dest: 'build/publicamundi.leaflet-src.js'
            }
        },
        uglify: {
            options: {
                banner: '/* <%= pkg.description %> version <%= pkg.version %> <%= grunt.template.today("yyyy-mm-dd") %> */\n',
                sourceMap: true
            },
            publicamundi: {
                src: 'build/publicamundi-src.js',
                dest: 'build/publicamundi.js'
            },
            openlayers: {
                src: 'build/publicamundi.ol-src.js',
                dest: 'build/publicamundi.ol.js'
            },
            leaflet: {
                src: 'build/publicamundi.leaflet-src.js',
                dest: 'build/publicamundi.leaflet.js'
            }
            /*files: {
              'build/publicamundi.min.js': ['build/publicamundi.js']
            }*/
        }
    });

    // Load the plugins
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');

    // Default task(s).
    grunt.registerTask('default', ['jshint', 'concat', 'uglify']);

};