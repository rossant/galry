//////////////////////////////////////
// JQUERY WHEEL
//////////////////////////////////////
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
//////////////////////////////////////
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
//////////////////////////////////////

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


//////////////////////////////////////
// GENERIC OPENGL FUNCTIONS
//////////////////////////////////////

// Deserializer
function deserializeScene(scene) {
    if (typeof scene == 'string')
        var scene = jQuery.parseJSON(scene);
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





// ACTION GENERATOR

var actionGenerator = function(myCanvas){//process_event, get_pos) {
    
    this.myCanvas = myCanvas;
    
    // this.process_event = process_event;
    // this.get_pos = get_pos;
    
    // console.log(this);
    // this.myCanvas = myCanvas;
    // this.process_event = myCanvas.process_event;
    // this.get_pos = myCanvas.get_pos;
    // console.log(this.get_pos);
    this.reset();
}



actionGenerator.prototype.clean_action = function() {
    this.action = false;
}

actionGenerator.prototype.reset = function() {
    this.action = false;
    this.key = false;
    this.key_modifier = false;
    this.mouse_button = 0;
    this.mouse_position = [0, 0];
    this.mouse_position_diff = [0, 0];
    this.mouse_press_position = [0, 0];
    this.wheel = 0;
    
    // console.log(this);
}

// callback functions
actionGenerator.prototype.mousedown = function(e) {
    this.mouse_button = e.which;
    this.mouse_press_position = this.myCanvas.get_pos(e);
    this.mouse_position = this.myCanvas.get_pos(e);
    this.myCanvas.process_event();
    return false;
}

actionGenerator.prototype.dblclick = function(e) {
    this.action = actions.DoubleClickAction;
    this.myCanvas.process_event();
}

actionGenerator.prototype.mouseup = function(e) {
    if (get_maximum_norm(this.mouse_position,
                this.mouse_press_position) < .01) {
        switch(e.which) {
            case 1:
                this.action = actions.LeftButtonClickAction;
                break;
            case 2:
                this.action = actions.MiddleButtonClickAction;
                break;
            case 3:
                this.action = actions.RightButtonClickAction;
                break;
        }
    }
    else {
        this.action = false;
    }
    this.mouse_button = 0;
    this.myCanvas.process_event();
    return false;
}

actionGenerator.prototype.mousemove = function(e) {
    var pos = this.myCanvas.get_pos(e);
    this.mouse_position_diff = [pos[0] - this.mouse_position[0],
                        pos[1] - this.mouse_position[1]];
    this.mouse_position = pos;
    if (get_maximum_norm(this.mouse_position,
                this.mouse_press_position) >= .01) {
        if (this.mouse_button == 1)
            this.action = actions.LeftButtonMouseMoveAction;
        else if (this.mouse_button == 2)
            this.action = actions.MiddleButtonMouseMoveAction;
        else if (this.mouse_button == 3)
            this.action = actions.RightButtonMouseMoveAction;
        else
            this.action = actions.MouseMoveAction;
    }
    this.myCanvas.process_event();
    return false;
}

actionGenerator.prototype.mousewheel = function(e, delta) {
    this.wheel = delta;
    this.action = actions.WheelAction;
    this.myCanvas.process_event();
    return false;
}

actionGenerator.prototype.keydown = function(e) {
    var key = e.which;
    if (key == 16 || key == 17 || key == 18) 
        this.key_modifier = key;
    else {
        this.action = actions.KeyPressAction;
        this.key = key;
    }
    this.myCanvas.process_event();
}

actionGenerator.prototype.keyup = function(e) {
    var key = e.which;
    if (key == 16 || key == 17 || key == 18) 
        this.key_modifier = false;
    else
        this.key = false;
    this.myCanvas.process_event();
}

actionGenerator.prototype.focusout = function(e) {
    this.reset();
}







var navigation = function() {
    this.tx = 0;
    this.ty = 0;
    this.tz = 0;
    this.sx = 1;
    this.sy = 1;
    this.sxl = 1;
    this.syl = 1;
    this.rx = 0;
    this.ry = 0;
}

navigation.prototype.reset = function() {
    // console.log(this);
    this.tx = 0;
    this.ty = 0;
    this.tz = 0;
    this.sx = 1;
    this.sy = 1;
    this.sxl = 1;
    this.syl = 1;
    this.rx = 0;
    this.ry = 0;
};

navigation.prototype.pan = function(dx, dy) {
    this.tx += dx / this.sx;
    this.ty += dy / this.sy;
}

navigation.prototype.rotate = function(dx, dy) {
    this.rx += dx;
    this.ry += dy;
}

navigation.prototype.zoom = function(dx, px, dy, py) {
    this.sx *= Math.exp(dx);
    this.sy *= Math.exp(dy);
    this.tx += -px * (1./this.sxl - 1./this.sx);
    this.ty += -py * (1./this.syl - 1./this.sy);
    this.sxl = this.sx;
    this.syl = this.sy;
}




//////////////////////////////////////
// GALRY CANVAS
//////////////////////////////////////
var galryCanvas = function(id, canvas, scene) {
    this.id = id;
    this.canvas = canvas;
    this.scene = scene;
}


galryCanvas.prototype.get_pos = function(e) {
    var offset = $('#' + this.id).offset();
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




// Initialize the shaders
galryCanvas.prototype.initShaders = function(vertex_shader_source, fragment_shader_source) {
    vertexShader = this.compileShader(vertex_shader_source, "VERTEX_SHADER");
    fragmentShader = this.compileShader(fragment_shader_source, "FRAGMENT_SHADER");

    var program = this.gl.createProgram();
    this.gl.attachShader(program, vertexShader);
    this.gl.attachShader(program, fragmentShader);
    this.gl.linkProgram(program);

    if (!this.gl.getProgramParameter(program, this.gl.LINK_STATUS))
    {
        window.alert("Could not initialise shaders");
    }

    this.gl.useProgram(program);
  
    return program;
}



// Process an interaction event and call the associated navigation methods
galryCanvas.prototype.process_event = function() {
    if (this.gen.action == actions.LeftButtonMouseMoveAction) {
        this.nav.pan(this.gen.mouse_position_diff[0], this.gen.mouse_position_diff[1]);
        this.draw();
    }
    if (this.gen.action == actions.RightButtonMouseMoveAction) {
        this.nav.zoom(this.gen.mouse_position_diff[0] * 2.5,
                 this.gen.mouse_press_position[0],
                 this.gen.mouse_position_diff[1] * 2.5,
                 this.gen.mouse_press_position[1]);
        this.draw();
    }
    if (this.gen.action == actions.WheelAction) {
        this.nav.zoom(this.gen.wheel * .2, 
                 this.gen.mouse_position[0],
                 this.gen.wheel * .2, 
                 this.gen.mouse_position[1]);
        this.draw();
    }
    if (this.gen.action == actions.KeyPressAction) {
        // R
        if (this.gen.key == 82) {
            this.nav.reset();
            this.draw();
        }
    }
}




// Initialize the OpenGL context within the canvas
galryCanvas.prototype.initGL = function() {
    // try
    // {
    var canvas = this.canvas;

    antialias = this.scene.renderer_options.antialias;
    this.gl = canvas.getContext("webgl", { antialias: antialias }) || canvas.getContext("experimental-webgl", { antialias: antialias });
    this.gl.viewportWidth = canvas.width;
    this.gl.viewportHeight = canvas.height;
    
    // global variables
    width = canvas.width;
    height = canvas.height;
    
    this.gl.clearColor(0.0, 0.0, 0.0, 1.0);
    
    this.setRenderingOptions();
    // }
    // catch (e)
    // {
    // }
    // if (!gl)
    // {
        // alert("Could not initialise WebGL, sorry :-(");
    // }
}

// Rendering options
galryCanvas.prototype.setRenderingOptions = function() {
    if (this.scene.renderer_options.transparency != false) {
        this.gl.enable(this.gl.BLEND);
        this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);
    }
    // if (scene.rendering_options.transparency != false) {
        // gl.enable(gl.BLEND);
        // gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    // }
    
}

// Compile a shader
galryCanvas.prototype.compileShader = function(source, type) {

    source = "precision mediump float;\n" + source;
    
    source = source.replace(/\\n/g, "\n")
    
    // console.log(source);
    
    // type is VERTEX_SHADER or FRAGMENT_SHADER
    var shader;
    shader = this.gl.createShader(this.gl[type]);

    this.gl.shaderSource(shader, source);
    this.gl.compileShader(shader);

    if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS))
    {
        window.alert(this.gl.getShaderInfoLog(shader));
        return null;
    }

    return shader;
}





// CORE
galryCanvas.prototype.initAction = function() {

    // USER ACTION GENERATOR
    this.gen = new actionGenerator(this);
    
    // NAVIGATION MANAGER
    this.nav = new navigation(this);

}



galryCanvas.prototype.init = function() {

    
    // Visuals and renderers
    this.visuals = [];
    this.renderers = [];

    // this.scene = scene;
    var scene = this.scene;
    
    // go through all visuals in the scene
    for (i in scene.visuals) {
        visual = scene.visuals[i];
        this.visuals = this.visuals.concat(visual);
        // create and initialize a new visual renderer
        vr = new visualRenderer(this);
        // vr.myCanvas = this;
        vr.nav = this.nav;
        vr.gl = this.gl;
        vr.init(visual);
        this.renderers = this.renderers.concat(vr);
    }
    
    this.gl.viewport(0, 0, this.gl.viewportWidth, this.gl.viewportHeight);
}
    
galryCanvas.prototype.draw = function() {
    // reset
    this.gl.clear(this.gl.COLOR_BUFFER_BIT);
    
    for (i in this.renderers) {
        this.renderers[i].draw();
    }
    
}




// VISUAL RENDERER
// ---------------
var visualRenderer = function(myCanvas) {
    this.myCanvas = myCanvas;
}


// Main methods
// ------------
visualRenderer.prototype.init = function(visual) {
    this.visual = visual;
    
    this.data_updating = [];

    this.program = this.myCanvas.initShaders(visual.vertex_shader, visual.fragment_shader);
    
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


// Variable methods
// ----------------
visualRenderer.prototype.get_variables = function(shader_type) {
    variables = [];
    for (i in this.visual.variables) {
        variable = this.visual.variables[i];
        if (shader_type != null && variable.shader_type == shader_type)
            variables = variables.concat(variable);
    }
    return variables;
}

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
    variable.location = this.gl.getAttribLocation(this.program, name);
    this.gl.enableVertexAttribArray(variable.location);
}

visualRenderer.prototype.init_uniform = function(name) {
    variable = this.get_variable(name);
    
    
    variable.location = this.gl.getUniformLocation(this.program, name);
}


// Load functions
// --------------
visualRenderer.prototype.load_attribute = function(name) {
    variable = this.get_variable(name);
    variable.buffer = this.gl.createBuffer();
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, variable.buffer);
    this.gl.bufferData(this.gl.ARRAY_BUFFER, variable.data, this.gl.STATIC_DRAW);
    // console.log("bind");
    // console.log(variable.buffer);
    // console.log(this.gl);
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
            this.gl[funname](loc, data);
            // console.log(data);
        }
        else if (ndim == 1) {
            this.gl[funname](loc, data);
        }
        else if (ndim == 2) {
            this.gl[funname](loc, data[0], data[1]);
        }
        else if (ndim == 3) {
            this.gl[funname](loc, data[0], data[1], data[2]);
        }
        else if (ndim == 4) {
            
            this.gl[funname](loc, data[0], data[1], data[2], data[3]);
        }
    }
    // matrix uniform
    else {
        var funname = "uniformmatrix" + ndim[0] + "fv";
        this.gl[funname](loc, 1, false, data);
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
        // console.log(data);
        
        update_funname = 'update_' + variable.shader_type;
        this[update_funname](name);      
    }
    this.data_updating = [];
}


// Buffer functions
// ----------------
visualRenderer.prototype.bind_buffer = function(name, offset) {
    variable = this.get_variable(name);
    // console.log(variable)
    // console.log(offset)
    this.gl.bindBuffer(this.gl.ARRAY_BUFFER, variable.buffer);
    this.gl.vertexAttribPointer(variable.location,
            variable.ndim, this.gl.FLOAT, false, 0, offset);
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


// Draw function
// -------------
visualRenderer.prototype.draw = function() {
    this.gl.viewport(0, 0, this.gl.viewportWidth, this.gl.viewportHeight);
    this.gl.clear(this.gl.COLOR_BUFFER_BIT);

    // bind all attribute buffers
    this.bind_buffers();
    
    // navigation
    this.set_data("translation", [this.nav.tx, this.nav.ty]);
    this.set_data("scale", [this.nav.sx, this.nav.sy]);

    // update all variables
    this.update_all_variables();

    
    
    // render stuff
    var bounds = this.visual.bounds;
    if (bounds.length <= 2) {
        // console.log(visual);
        this.gl.drawArrays(this.gl[this.visual.primitive_type], bounds[0], bounds[1] - bounds[0]);
        // this.gl.drawArrays(gl[this.visual.primitive_type], 0, 0);
    }
    else {
        // console.log(bounds);
        // multiDrawArrays not available
        for (var i = 0; i < bounds.length - 1; i++) {
            
            this.bind_buffers(bounds[i]);
    
            this.gl.drawArrays(this.gl[this.visual.primitive_type], 0, bounds[i + 1] - bounds[i]);
        }
    }
}





var canvasList = [];

// Main function
var initGalry = function(id, scene) {
    // id = mid;
    // this.id = id;
    sid = '#' + id;
    canvas = document.getElementById(id);
    // Disable right click context menu on the canvas.
    $(document).oncontextmenu = function() {return false;};
    
    $(document).ready(function(){ 
            document.oncontextmenu = function() {return false;};
    });
    
    var myCanvas = new galryCanvas(id, canvas, scene);
    
    
    myCanvas.initAction();
    
    // mouse bindings bindings
    $(sid).mousedown(function (e) {myCanvas.gen.mousedown(e);});
    $(sid).dblclick(function (e) {myCanvas.gen.dblclick(e);});
    // $('canvas').mouseup(myCanvas.gen.mouseup);
    // $('canvas').mousemove(myCanvas.gen.mousemove);
    $(sid).mousewheel(function (e) {myCanvas.gen.mousewheel(e);});
    
    // others
    $(sid).focusout(function (e) {myCanvas.gen.focusout(e);});        
    
    // keyboard bindings
    $(sid).keydown(function (e) {myCanvas.gen.keydown(e);});
    $(sid).keyup(function (e) {myCanvas.gen.keyup(e);});
    
    // allow to move the mouse outside the canvas
    $(document).mousemove(function (e) {myCanvas.gen.mousemove(e);});
    // $(document).mousemove(function (e) { console.log(this); });
    $(document).mouseup(function (e) {myCanvas.gen.mouseup(e); return false;});
        
    
    
    
    
    
    myCanvas.initGL();
    myCanvas.init();
    myCanvas.draw();
    
    canvasList = canvasList.concat(myCanvas);
}




//////////////////////////////////////
// IPYTHON NOTEBOOK
//////////////////////////////////////
// Javascript handler.
// This function takes the json object and the cell DOM element as inputs.
// It can perform modifications to the DOM element in order to display
// something, using the information stored in the JSON object.
var galry_handler = function (json, element)
{
    // DOM id
    id = 'Galry-' + IPython.utils.uuid();
    // id = 'galry-canvas';
    
    // console.log(id);
    
    // Create a DIV HTML object to insert in the cell.
    var toinsert = $("<canvas/>").attr('id',id).attr('tabindex',1)
        .attr('width', 600)
        .attr('height', 400)
        .attr('style', "border: 1px solid black;");
        
    element.append(toinsert);
    
    
    // json = json;
    //element.append("<div/>").attr('id','debug').html('hey');
    
    // console.log(json);
    scene = deserializeScene(json);
    // scene = json;

    // console.log(scene);
    
    initGalry(id, scene);
    
};

// Link the handler name to the javascript function which performs
// some actions to display the object.
if (typeof IPython !== 'undefined')
    IPython.json_handlers.register_handler('GalryPlotHandler', galry_handler);
