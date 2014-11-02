(function (window, $) {
    "use strict";

    // PublicaMundi namespace
    var PublicaMundi = {
        __namespace: 'PublicaMundi'
    };

    // Relative path to this script
    var _relativePath = null;

    // Default library to use
    var _defaultLib = null;

    // Scripts to load
    var _scripts = [];
    var _loadingScript = null;

    // Available layer types
    PublicaMundi.LayerType = {
        WMS: 'WMS',
        WFS: 'WFS',
        TILE: 'Tile',
        GeoJSON: 'GeoJSON',
        KML: 'KML',
        GPX: 'GPX',
        CSV: 'CSV',
        WCS: 'WCS',
        WCPS: 'WCPS'
    };

    // Version
    PublicaMundi.version = '0.0.1';

    // Define a new namespace using dot (.) notation e.g. PublicaMundi.Layer.WFS
    PublicaMundi.define = function (namespace) {
        if (!namespace) return;
        var parts = namespace.split('.');

        for (var current = window, index = 0; index < parts.length; index++) {
            if (!parts[index]) {
                continue;
            }
            if (typeof current[parts[index]] === 'undefined') {
                current[parts[index]] = {
                    __namespace: parts.slice(0, index + 1).join('.')
                };
            }
            current = current[parts[index]];
        }
    };

    var _extend = function (target, source) {
        if (source) {
            for (var property in source) {
                if ((source.hasOwnProperty(property)) && (source[property] !== undefined)) {
                    target[property] = source[property];
                }
            }
        }

        return target;
    };

    // Class inheritance based on OpenLayers 2.x
    // Declare base Class. Javascript is not an object oriented language. We are simulating classes and
    // inheritance using this class.
    // In order to create a new class we use the following syntax:
    //
    // var newClass = ChemSafe.Class(prototype);
    //
    // The call above will return a new Function object that will be used as our new Class constructor.
    // To create a new class with multiple inheritance, use the following syntax:
    //
    // var newClass = ChemSafe.Class(Class1, Class2, ... , ClassN, prototype);
    //
    // Note that instanceof reflection will only reveil Class1 as superclass. Class2 to ClassN are mixins.
    // All the properties and methods added to the prototype parameter will become members of the new Class
    // prototype.
    PublicaMundi.Class = function () {
        var classes = arguments;

        // This is the new class we are going to create. The new class is actuall a Function object.
        // Every Class created with this method is expected to have an initialize() method. Also the derived
        // classes are responsible for calling their parent class initialize method. The initialize() method
        // is used for setting 'private' members using this.property = value assignments.   
        var Class = function () {
            if (typeof this.initialize === 'function') {
                this.initialize.apply(this, arguments);
            }
        };

        // New class prototype
        var prototype = {};
        // Last parent class and helper variable for storing parent class initilize() method reference.
        var parent, initialize;

        var _initialize = function () { };

        // Start adding functionality to our class
        for (var i = 0, len = arguments.length; i < len; ++i) {
            // Check if the given argument is of type function; Hence it is a base "Class"
            if (typeof arguments[i] === "function") {
                // Make the class passed as the first argument the superclass. By doing so,
                // we have to create a new instance of this class and set it as the prototype of
                // our new class.
                if (i === 0 && len > 1) {
                    // Create a reference to the parent class initialize method. As mentioned earlier this method
                    // is used for setting private members. We dont want to create this members right now as they 
                    // will be created when we create actual instances of our new class.
                    initialize = arguments[i].prototype.initialize;
                    // Replace the initialize method with an empty function,
                    // because we do not want to create a real instance here
                    arguments[i].prototype.initialize = _initialize();
                    // The line below makes sure that the new class has a
                    // superclass
                    prototype = new arguments[i]();
                    prototype.constructor = Class;
                    // Restore the original initialize method
                    if (initialize === undefined) {
                        delete arguments[i].prototype.initialize;
                    } else {
                        arguments[i].prototype.initialize = initialize;
                    }
                }
                // Get the prototype of the superclass
                parent = arguments[i].prototype;
            } else {
                // In this case we're extending with the prototype
                parent = arguments[i];
            }
            // By extending the class prototype with the parent prototype all the methods and properties of the
            // two classess are merged.
            _extend(prototype, parent);
        }
        // Set new class prototype. The  'prototype' object has gathered the properties and functions
        // of all the parent classes.
        Class.prototype = prototype;
        Class.prototype.constructor = Class;

        return Class;
    };


    // Methods and properties for resolving mapping frameworks
    var _resolvers = {};

    PublicaMundi.registerFrameworkResolver = function (name, resolver) {
        if (_resolvers.hasOwnProperty(name)) {
            console.log('Resolver for framework ' + name + ' already registered.');
            return false;
        }

        _resolvers[name] = resolver;

        return true;
    };

    PublicaMundi.resolveFramework = function () {
        for (var name in _resolvers) {
            if (_resolvers[name]()) {
                return name;
            }
        }
        return null;
    };

    // Helper functions
    PublicaMundi.isDefined = function (arg) {
        return (typeof arg !== 'undefined');
    };

    PublicaMundi.isFunction = function (arg) {
        return (typeof arg === 'function');
    };

    PublicaMundi.isObject = function (arg) {
        return (typeof arg === 'object');
    };

    PublicaMundi.isClass = function (arg) {
        var parts = arg.split('.');
        for (var current = window, index = 0; index < parts.length; index++) {
            if ((!parts[index]) || (typeof current[parts[index]] === 'undefined')) {
                return false;
            }
            if ((index === parts.length - 1) && (typeof current[parts[index]] !== 'function')) {
                return false;
            }
            current = current[parts[index]];
        }

        return true;
    };

    PublicaMundi.isArray = function (arg) {
        if (!Array.isArray) {
            return Object.prototype.toString.call(arg) === '[object Array]';
        }
        return Array.isArray(arg);
    };

    PublicaMundi.getQueryStringParameters = function (url) {
        var parameters = {};
        url.replace(
            new RegExp("([^?=&]+)(=([^&#]*))?", "g"),
            function ($0, $1, $2, $3) { parameters[$1] = $3; }
        );

        return parameters;
    };

    // Locator service used for implementing Dependency Injection. Types (including their namespace) 
    // are associated to a function (constructor/class)
    PublicaMundi.locator = {
        _dependencies: [],
        _factories: [],
        register: function (type, factory) {
            var index = this._dependencies.indexOf(type);
            if (index < 0) {
                this._dependencies.push(type);
                this._factories.push(factory);
            } else {
                this._factories[index] = factory;
            }

            return factory;
        },
        unregister: function (type) {
            var index = this._dependencies.indexOf(type);
            if (index >= 0) {
                this._dependencies.splice(index, 1);
                this._factories.splice(index, 1);
            }
        },
        resolve: function (type) {
            var index = this._dependencies.indexOf(type);
            if (index < 0) {
                return null;
            }
            return this._factories[index];
        },
        create: function (type, options) {
            var Factory = this.resolve(type);
            if (Factory) {
                return new Factory(options);
            }
            return null;
        }
    };

    /*

    // Layer type registration

    var registration = {
        // Layer type
        layer: PublicaMundi.LayerType.WMS,
        // Framework
        framework: OpenLayers,
        // Class type
        type: 'PublicaMundi.OpenLayers.Layer.WMS',
        // Constructor
        factory: function () { }
    };

    */

    PublicaMundi.registry = {
        _LayerTypeRegistry: [],
        registerLayerType: function (options) {
            var registration = null;

            for (var index = 0; index < this._LayerTypeRegistry.length; index++) {
                if ((this._LayerTypeRegistry[index].layer === options.layer) &&
                   (this._LayerTypeRegistry[index].framework === options.framework)) {
                    registration = this._LayerTypeRegistry[index];
                    break;
                }
            }
            if (registration) {
                registration.type = options.type;
            } else {
                registration = {
                    layer: options.layer,
                    framework: options.framework,
                    type: options.type
                };
                this._LayerTypeRegistry.push(registration);
            }
            PublicaMundi.locator.register(options.type, options.factory);
        },
        resolveLayerType: function (layer) {
            var registration = null;

            // TODO : Resolve framework only once during loading?
            var framework = PublicaMundi.resolveFramework();

            for (var index = 0; index < this._LayerTypeRegistry.length; index++) {
                if ((this._LayerTypeRegistry[index].layer === layer) &&
                   (this._LayerTypeRegistry[index].framework === framework)) {
                    registration = this._LayerTypeRegistry[index];
                    break;
                }
            }

            if (registration) {
                return registration.type;
            }
            return null;
        },
        createLayer: function (options) {
            // TODO : Handle dynamic layer detection
            var type = this.resolveLayerType(options.type);

            if (type) {
                return PublicaMundi.locator.create(type, options);
            }
            return null;
        },
        getFactories: function () {
            return this._LayerTypeRegistry.map(function (m) {
                return PublicaMundi.locator.resolve(m.type);
            });
        }
    };

    // Allow to restore existing variables
    PublicaMundi._PM = window.PM;

    PublicaMundi.noConflict = function () {
        if (window.PM === PublicaMundi) {
            if (typeof this._PM !== 'undefined') {
                window.PM = this._PM;
            } else {
                delete window.PM;
            }
        }
        return this;
    };

    // This solution will not work if a module loader is used or scripts are loaded with
    // the defer/async attribute ...
    _relativePath = jQuery('script').last().attr('src');
    _relativePath = _relativePath.substring(0, _relativePath.lastIndexOf('/') + 1);

    // Get default library
    _defaultLib = jQuery('script').last().data('library');
    if (!_defaultLib) {
        _defaultLib = 'ol';
    }

    // Function for handling asynchronous resource loading
    PublicaMundi.ready = function (method) {
        if (!PublicaMundi.isFunction(method)) {
            console.log('Argument for ready() is not a function.');
            return;
        }

        // Load default scripts
        if (!PublicaMundi.resolveFramework()) {
            console.log('Loading scripts...');

            $('<link/>', {
                rel: 'stylesheet',
                type: 'text/css',
                href: _relativePath + 'lib/' + _defaultLib + '/' + _defaultLib + '.css'
            }).appendTo('head');

            _scripts.push(_relativePath + 'lib/' + _defaultLib + '/' + _defaultLib + '.js');
            _scripts.push(_relativePath + 'publicamundi.' + _defaultLib + '.js');
        }

        if (_scripts.length === 0) {
            method();
        } else {
            var loader = function () {
                if (_loadingScript) {
                    console.log('[' + _loadingScript + '] has been loaded.');
                    _loadingScript = null;
                }
                if (_scripts.length > 0) {
                    _loadingScript = _scripts[0];
                    _scripts.shift();
                    $.ajax({
                        url: _loadingScript,
                        dataType: "script",
                        success: loader,
                        cache: true
                    });
                } else {
                    method();
                }
            };
            loader();
        }
    };

    window.PublicaMundi = window.PM = PublicaMundi;
})(window, jQuery);