// TODO: support for multiple JS files



//////////////////////////////////////
// JQUERY WHEEL

/*! Copyright (c) 2011 Brandon Aaron (http://brandonaaron.net)
 * Licensed under the MIT License (LICENSE.txt).
 *
 * Thanks to: http://adomas.org/javascript-mouse-wheel/ for some pointers.
 * Thanks to: Mathias Bank(http://www.mathias-bank.de) for a scope bug fix.
 * Thanks to: Seamus Leahy for adding deltaX and deltaY
 *
 * Version: 3.0.6
 * 
 * Requires: 1.2.2+
 */

(function($) {

var types = ['DOMMouseScroll', 'mousewheel'];

if ($.event.fixHooks) {
    for ( var i=types.length; i; ) {
        $.event.fixHooks[ types[--i] ] = $.event.mouseHooks;
    }
}

$.event.special.mousewheel = {
    setup: function() {
        if ( this.addEventListener ) {
            for ( var i=types.length; i; ) {
                this.addEventListener( types[--i], handler, false );
            }
        } else {
            this.onmousewheel = handler;
        }
    },
    
    teardown: function() {
        if ( this.removeEventListener ) {
            for ( var i=types.length; i; ) {
                this.removeEventListener( types[--i], handler, false );
            }
        } else {
            this.onmousewheel = null;
        }
    }
};

$.fn.extend({
    mousewheel: function(fn) {
        return fn ? this.bind("mousewheel", fn) : this.trigger("mousewheel");
    },
    
    unmousewheel: function(fn) {
        return this.unbind("mousewheel", fn);
    }
});


function handler(event) {
    var orgEvent = event || window.event, args = [].slice.call( arguments, 1 ), delta = 0, returnValue = true, deltaX = 0, deltaY = 0;
    event = $.event.fix(orgEvent);
    event.type = "mousewheel";
    
    // Old school scrollwheel delta
    if ( orgEvent.wheelDelta ) { delta = orgEvent.wheelDelta/120; }
    if ( orgEvent.detail     ) { delta = -orgEvent.detail/3; }
    
    // New school multidimensional scroll (touchpads) deltas
    deltaY = delta;
    
    // Gecko
    if ( orgEvent.axis !== undefined && orgEvent.axis === orgEvent.HORIZONTAL_AXIS ) {
        deltaY = 0;
        deltaX = -1*delta;
    }
    
    // Webkit
    if ( orgEvent.wheelDeltaY !== undefined ) { deltaY = orgEvent.wheelDeltaY/120; }
    if ( orgEvent.wheelDeltaX !== undefined ) { deltaX = -1*orgEvent.wheelDeltaX/120; }
    
    // Add event and delta to the front of the arguments
    args.unshift(event, delta, deltaX, deltaY);
    
    return ($.event.dispatch || $.event.handle).apply(this, args);
}

})(jQuery);



//////////////////////////////////////
// DATA

// Base64 decoder
var Base64Binary = {
	_keyStr : "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",

	/* will return a  Uint8Array type */
	decodeArrayBuffer: function(input) {
		var bytes = (input.length/4) * 3;
		var ab = new ArrayBuffer(bytes);
		this.decode(input, ab);

		return ab;
	},

	decode: function(input, arrayBuffer) {
		//get last chars to see if are valid
		var lkey1 = this._keyStr.indexOf(input.charAt(input.length-1));		 
		var lkey2 = this._keyStr.indexOf(input.charAt(input.length-2));		 
        
		var bytes = (input.length/4) * 3;
		if (lkey1 == 64) bytes--; //padding chars, so skip
		if (lkey2 == 64) bytes--; //padding chars, so skip

		var uarray;
		var chr1, chr2, chr3;
		var enc1, enc2, enc3, enc4;
		var i = 0;
		var j = 0;

		if (arrayBuffer)
			uarray = new Uint8Array(arrayBuffer);
		else
			uarray = new Uint8Array(bytes);

		input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

		for (i=0; i<bytes; i+=3) {	
			//get the 3 octets in 4 ascii chars
			enc1 = this._keyStr.indexOf(input.charAt(j++));
			enc2 = this._keyStr.indexOf(input.charAt(j++));
			enc3 = this._keyStr.indexOf(input.charAt(j++));
			enc4 = this._keyStr.indexOf(input.charAt(j++));

			chr1 = (enc1 << 2) | (enc2 >> 4);
			chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
			chr3 = ((enc3 & 3) << 6) | enc4;

			uarray[i] = chr1;			
			if (enc3 != 64) uarray[i+1] = chr2;
			if (enc4 != 64) uarray[i+2] = chr3;
		}

		return uarray;	
	}
}

// Convert a Base64-encoded array into a Javascript Array Buffer.
function get_array(s, vartype) {
    data = Base64Binary.decodeArrayBuffer(s);
    size = Math.floor(data.byteLength / 4);
    // 32 bits floats
    if (vartype == 'float')
        data = new Float32Array(data, 0, size);
    // 32 bits int
    else if (vartype == 'int')
        // HACK: we force int32 to be float32 for OpenGL ES
        data = new Float32Array(new Int32Array(data, 0, size));
    return data;
}



//////////////////////////////////////
// USER ACTIONS

function get_pos(e) {
    var offset = $("#" + id).offset();
    if (offset == undefined) {
        // console.log("id is undefined" + id);
        return [0, 0];
    }
    var x = e.pageX - offset.left;
    var y = e.pageY - offset.top;
    x = 2 * x / width - 1;
    y = -(2 * y / height - 1);
    return [x, y];
}

// Return the inf norm between two points.
function get_maximum_norm(p1, p2) {
    var m = Math.max(Math.abs(p1[0]-p2[0]), Math.abs(p1[1]-p2[1]));
    return m;
}


// ctrl, shift, alt
var key_modifiers = {
    Ctrl: 17,
    Shift: 16,
    Alt: 18,};

var actions = {
    MouseMoveAction: 0,
    LeftButtonClickAction: 1,
    MiddleButtonClickAction: 2,
    RightButtonClickAction: 3,
    LeftButtonMouseMoveAction: 4,
    MiddleButtonMouseMoveAction: 5,
    RightButtonMouseMoveAction: 6,
    DoubleClickAction: 7,
    WheelAction: 8,
    KeyPressAction: 9,
};

var gen = {
    // fields
    action: false,
    key: false,
    key_modifier: false,
    mouse_button: 0,
    mouse_position: [0, 0],
    mouse_position_diff: [0, 0],
    mouse_press_position: [0, 0],
    wheel: 0,
    
    clean_action: function() {
        gen.action = false;
    },
    
    reset: function() {
        gen.action = false;
        gen.key = false;
        gen.key_modifier = false;
        gen.mouse_button = 0;
        gen.mouse_position = [0, 0];
        gen.mouse_position_diff = [0, 0];
        gen.mouse_press_position = [0, 0];
        gen.wheel = 0;
    },
    
    // callback functions
    mousedown: function(e) {
        gen.mouse_button = e.which;
        gen.mouse_press_position = get_pos(e);
        gen.mouse_position = get_pos(e);
        process_event();
        return false;
    },
    
    dblclick: function(e) {
        gen.action = actions.DoubleClickAction;
        process_event();
    },
    
    mouseup: function(e) {
        if (get_maximum_norm(gen.mouse_position,
                    gen.mouse_press_position) < .01) {
            switch(e.which) {
                case 1:
                    gen.action = actions.LeftButtonClickAction;
                    break;
                case 2:
                    gen.action = actions.MiddleButtonClickAction;
                    break;
                case 3:
                    gen.action = actions.RightButtonClickAction;
                    break;
            }
        }
        else {
            gen.action = false;
        }
        gen.mouse_button = 0;
        process_event();
        return false;
    },
    
    mousemove: function(e) {
        var pos = get_pos(e);
        gen.mouse_position_diff = [pos[0] - gen.mouse_position[0],
                            pos[1] - gen.mouse_position[1]];
        gen.mouse_position = pos;
        if (get_maximum_norm(gen.mouse_position,
                    gen.mouse_press_position) >= .01) {
            if (gen.mouse_button == 1)
                gen.action = actions.LeftButtonMouseMoveAction;
            else if (gen.mouse_button == 2)
                gen.action = actions.MiddleButtonMouseMoveAction;
            else if (gen.mouse_button == 3)
                gen.action = actions.RightButtonMouseMoveAction;
            else
                gen.action = actions.MouseMoveAction;
        }
        process_event();
        return false;
    },
    
    mousewheel: function(e, delta) {
        gen.wheel = delta;
        gen.action = actions.WheelAction;
        process_event();
        return false;
    },
    
    keydown: function(e) {
        var key = e.which;
        if (key == 16 || key == 17 || key == 18) 
            gen.key_modifier = key;
        else {
            gen.action = actions.KeyPressAction;
            gen.key = key;
        }
        process_event();
    },
    
    keyup: function(e) {
        var key = e.which;
        if (key == 16 || key == 17 || key == 18) 
            gen.key_modifier = false;
        else
            gen.key = false;
        process_event();
    },
    
    focusout: function(e) {
        gen.reset();
    },
};





//////////////////////////////////////
// NAV

nav = {

    tx: 0,
    ty: 0,
    tz: 0,
    sx: 1,
    sy: 1,
    sxl: 1,
    syl: 1,
    rx: 0,
    ry: 0,

    reset: function() {
        nav.tx = 0;
        nav.ty = 0;
        nav.tz = 0;
        nav.sx = 1;
        nav.sy = 1;
        nav.sxl = 1;
        nav.syl = 1;
        nav.rx = 0;
        nav.ry = 0;
    },

    pan: function(dx, dy) {
        nav.tx += dx / nav.sx;
        nav.ty += dy / nav.sy;
    },

    rotate: function(dx, dy) {
        nav.rx += dx;
        nav.ry += dy;
    },

    zoom: function(dx, px, dy, py) {
        nav.sx *= Math.exp(dx);
        nav.sy *= Math.exp(dy);
        nav.tx += -px * (1./nav.sxl - 1./nav.sx);
        nav.ty += -py * (1./nav.syl - 1./nav.sy);
        nav.sxl = nav.sx;
        nav.syl = nav.sy;
    },
}


// Process an interaction event and call the associated navigation methods
function process_event() {
    if (gen.action == actions.LeftButtonMouseMoveAction) {
        nav.pan(gen.mouse_position_diff[0], gen.mouse_position_diff[1]);
        renderer.draw();
    }
    if (gen.action == actions.RightButtonMouseMoveAction) {
        nav.zoom(gen.mouse_position_diff[0] * 2.5,
                 gen.mouse_press_position[0],
                 gen.mouse_position_diff[1] * 2.5,
                 gen.mouse_press_position[1]);
        renderer.draw();
    }
    if (gen.action == actions.WheelAction) {
        nav.zoom(gen.wheel * .2, 
                 gen.mouse_position[0],
                 gen.wheel * .2, 
                 gen.mouse_position[1]);
        renderer.draw();
    }
    if (gen.action == actions.KeyPressAction) {
        // R
        if (gen.key == 82) {
            nav.reset();
            renderer.draw();
        }
    }
}



//////////////////////////////////////
// GL

// WebGL context
var gl = null;
var id = 'canvas';
var scene = null;


// GENERIC OPENGL FUNCTIONS
// ------------------------
// Initialize the OpenGL context within the canvas
function initGL(canvas) {
    try
    {
        antialias = scene.renderer_options.antialias;
        gl = canvas.getContext("webgl", { antialias: antialias }) || canvas.getContext("experimental-webgl", { antialias: antialias });
        gl.viewportWidth = canvas.width;
        gl.viewportHeight = canvas.height;
        
        // global variables
        width = canvas.width;
        height = canvas.height;
        
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        
        setRenderingOptions();
    }
    catch (e)
    {
    }
    if (!gl)
    {
        alert("Could not initialise WebGL, sorry :-(");
    }
}

// Rendering options
function setRenderingOptions() {
    if (scene.renderer_options.transparency != false) {
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    }
    // if (scene.rendering_options.transparency != false) {
        // gl.enable(gl.BLEND);
        // gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    // }
    
}

// Compile a shader
function compileShader(source, type) {

    source = "precision mediump float;\n" + source;

    // type is VERTEX_SHADER or FRAGMENT_SHADER
    var shader;
    shader = gl.createShader(gl[type]);

    gl.shaderSource(shader, source);
    gl.compileShader(shader);

    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS))
    {
        window.alert(gl.getShaderInfoLog(shader));
        return null;
    }

    return shader;
}

// Initialize the shaders
function initShaders(vertex_shader_source, fragment_shader_source) {
    vertexShader = compileShader(vertex_shader_source, "VERTEX_SHADER");
    fragmentShader = compileShader(fragment_shader_source, "FRAGMENT_SHADER");

    var program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS))
    {
        window.alert("Could not initialise shaders");
    }

    gl.useProgram(program);
  
    return program;
}

// Deserializer
function deserializeScene(scene_json) {
    var scene = jQuery.parseJSON(scene_json);
    for (i in scene.visuals) {
        v = scene.visuals[i];
        if (typeof(v.bounds) == 'string')
            v.bounds = get_array(v.bounds, 'int');
        for (j in v.variables) {
            variable = v.variables[j];
            type = variable.shader_type;
            if (type == 'attribute' || type == 'uniform') {
                vartype = variable.vartype;
                // attribute: we force float
                // if (type == 'attribute')
                    // vartype = 'float';
                if (typeof(variable.data) == 'string') {
                    variable.data = get_array(variable.data, vartype);
                }
            }
        }
    }
    return scene;
}





// VISUAL RENDERER
// ---------------
var visualRenderer = function() { }


// Main methods
// ------------
visualRenderer.prototype.init = function(visual) {
    this.visual = visual;
    
    this.data_updating = [];

    this.program = initShaders(visual.vertex_shader, visual.fragment_shader);
    
    // initialize variables
    for (i in visual.variables) {
        variable = visual.variables[i];
        if (variable.shader_type == 'attribute' || variable.shader_type == 'uniform') {
            init_funname = 'init_' + variable.shader_type;
            this[init_funname](variable.name);
        }
    }
    
    // load variables
    for (i in visual.variables) {
        variable = visual.variables[i];
        if (variable.shader_type == 'attribute' || variable.shader_type == 'uniform') {
            load_funname = 'load_' + variable.shader_type;
            this[load_funname](variable.name);
        }
    }
}

visualRenderer.prototype.draw = function() {
    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // bind all attribute buffers
    this.bind_buffers();
    
    // navigation
    this.set_data("translation", [nav.tx, nav.ty]);
    this.set_data("scale", [nav.sx, nav.sy]);

    // update all variables
    this.update_all_variables();

    // render stuff
    var bounds = this.visual.bounds;
    if (bounds.length <= 2) {
        gl.drawArrays(gl[this.visual.primitive_type], bounds[0], bounds[1] - bounds[0]);
    }
    else {
        // multiDrawArrays not available
        for (var i = 0; i < bounds.length - 1; i++) {
            
            this.bind_buffers(bounds[i]);
    
            gl.drawArrays(gl[this.visual.primitive_type], 0, bounds[i + 1] - bounds[i]);
        }
    }
}


// Variable methods
// ----------------
// get variables
visualRenderer.prototype.get_variables = function(shader_type) {
    variables = [];
    for (i in this.visual.variables) {
        variable = this.visual.variables[i];
        if (shader_type != null && variable.shader_type == shader_type)
            variables = variables.concat(variable);
    }
    return variables;
}

// get variable
visualRenderer.prototype.get_variable = function(name) {
    for (i in this.visual.variables) {
        variable = this.visual.variables[i];
        if (variable.name == name)
            return variable;
    }
}


// Initialization functions
// ------------------------
visualRenderer.prototype.init_attribute = function(name) {
    variable = this.get_variable(name);
    variable.location = gl.getAttribLocation(this.program, name);
    gl.enableVertexAttribArray(variable.location);
}

visualRenderer.prototype.init_uniform = function(name) {
    variable = this.get_variable(name);
    variable.location = gl.getUniformLocation(this.program, name);
}


// Load functions
// --------------
visualRenderer.prototype.load_attribute = function(name) {
    variable = this.get_variable(name);
    variable.buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, variable.buffer);
    // console.log(variable.data);
    gl.bufferData(gl.ARRAY_BUFFER, variable.data, gl.STATIC_DRAW);
}

visualRenderer.prototype.load_uniform = function(name) {
    variable = this.get_variable(name);
    var ndim = variable.ndim;
    var size = variable.size;
    var vartype = variable.vartype;
    var data = variable.data;
    
    var float_suffix = {true: 'f', false: 'i'};
    var array_suffix = {true: 'v', false: ''};
        
    loc = variable.location;
    // scalar or vector uniform
    if (!(ndim instanceof Array)) {
        var funname = "uniform" + ndim + float_suffix[vartype == 'float'] + 
            array_suffix[size > 0];
        if (size > 0) {
            gl[funname](loc, data);
            // console.log(data);
        }
        else if (ndim == 1) {
            gl[funname](loc, data);
        }
        else if (ndim == 2) {
            gl[funname](loc, data[0], data[1]);
        }
        else if (ndim == 3) {
            gl[funname](loc, data[0], data[1], data[2]);
        }
        else if (ndim == 4) {
            
            gl[funname](loc, data[0], data[1], data[2], data[3]);
        }
    }
    // matrix uniform
    else {
        var funname = "uniformmatrix" + ndim[0] + "fv";
        gl[funname](loc, 1, false, data);
    }
}


// Update functions
// ----------------
visualRenderer.prototype.set_data = function(name, data) {
    variable = this.get_variable(name);
    variable.data = data;
    this.data_updating = this.data_updating.concat(name);
}

visualRenderer.prototype.update_attribute = function(name) {
    console.log("WARNING: updating attribute not implemented yet");
}

visualRenderer.prototype.update_uniform = function(name) {
    this.load_uniform(name);
}

visualRenderer.prototype.update_all_variables = function() {
    for (i in this.data_updating) {
        name = this.data_updating[i];
        variable = this.get_variable(name);
        data = variable.data;
        
        // console.log("updating variable " + name);
        update_funname = 'update_' + variable.shader_type;
        this[update_funname](name);      
    }
    this.data_updating = [];
}




// Buffer functions
// ----------------
visualRenderer.prototype.bind_buffer = function(name, offset) {
    variable = this.get_variable(name);
    gl.bindBuffer(gl.ARRAY_BUFFER, variable.buffer);
    gl.vertexAttribPointer(variable.location,
            variable.ndim, gl.FLOAT, false, 0, offset);
}

visualRenderer.prototype.bind_buffers = function(offset) {
    variables = this.get_variables('attribute');
    if (offset == null)
        offset = 0;
    for (i in variables) {
        name = variables[i].name;
        offset2 = offset * variables[i].ndim * 4
        this.bind_buffer(name, offset2);
    }
}


// Renderer
// --------
var renderer = {
    
    visuals: [],
    renderers: [],

    // Initialization
    init: function(scene) {
        this.scene = scene;
        // go through all visuals in the scene
        for (i in scene.visuals) {
            visual = scene.visuals[i];
            this.visuals = this.visuals.concat(visual);
            // create and initialize a new visual renderer
            vr = new visualRenderer();
            vr.init(visual);
            this.renderers = this.renderers.concat(vr);
        }
        gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    },
    
    // Draw
    draw: function() {
        // reset
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        for (i in this.renderers) {
            this.renderers[i].draw();
        }
        
    },
    
};




//////////////////////////////////////
// CORE
// Main function
function webGLStart(id) {
    var canvas = document.getElementById(id);
    
    // Disable right click context menu on the canvas.
    // $(document).oncontextmenu = function() {return false;};
    
    $(document).ready(function(){ 
            document.oncontextmenu = function() {return false;};
    });
    
    // mouse bindings bindings
    $('canvas').mousedown(gen.mousedown);
    $('canvas').dblclick(gen.dblclick);
    $('canvas').mouseup(gen.mouseup);
    $('canvas').mousemove(gen.mousemove);
    $('canvas').mousewheel(gen.mousewheel);
    
    // others
    $('canvas').focusout(gen.focusout);        
    
    // keyboard bindings
    $(document).keydown(gen.keydown);
    $(document).keyup(gen.keyup);
    
    // allow to move the mouse outside the canvas
    $(document).mousemove(gen.mousemove);
    $(document).mouseup(gen.mouseup);
        
    // Initialize everything
    initGL(canvas);
    
    // call renderer(scene).init/draw
    renderer.init(scene);
    renderer.draw();
}



/*

// Javascript handler.
// This function takes the json object and the cell DOM element as inputs.
// It can perform modifications to the DOM element in order to display
// something, using the information stored in the JSON object.
var galry_handler = function (json, element)
{
    // DOM id
    id = 'Galry-' + IPython.utils.uuid();
    
    // Create a DIV HTML object to insert in the cell.
    var toinsert = $("<canvas/>").attr('id',id).attr('tabindex',1)
        .attr('width', width)
        .attr('height', height)
        .attr('style', "border: 1px solid black;");
        
    element.append(toinsert);
    
    json = json;
    visual = json['visual'];
    dataholder = json['dataholder'];
    
    //element.append("<div/>").attr('id','debug').html('hey');
    
    webGLStart(id);
    
};

// Link the handler name to the javascript function which performs
// some actions to display the object.
IPython.json_handlers.register_handler('GalryPlotHandler', galry_handler);
*/