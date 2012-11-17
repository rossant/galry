// WebGL context
var gl;

// Shader program
var shaderProgram;

// Initialize the OpenGL context within the canvas
function initGL(canvas) {
    try
    {
        gl = canvas.getContext("webgl", { antialias: antialias }) || canvas.getContext("experimental-webgl", { antialias: antialias });
        gl.viewportWidth = canvas.width;
        gl.viewportHeight = canvas.height;
    }
    catch (e)
    {
    }
    if (!gl)
    {
        alert("Could not initialise WebGL, sorry :-(");
    }
}

// DATA LOADER
var dataloader = {
    init_attribute: function(name) {
        template.attributes[name].location = gl.getAttribLocation(shaderProgram, name);
        gl.enableVertexAttribArray(template.attributes[name].location);
    },

    init_uniform: function(name) {
        template.uniforms[name].location = gl.getUniformLocation(shaderProgram, name);
    },
    
    // upload upload_attribute data
    upload_attribute: function(name, data, size) {
        if (data == undefined)
            data = dataholder[name];
        if (size == undefined)
            size = dataholder[size];
        template.attributes[name].buffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, template.attributes[name].buffer);
        gl.bufferData(gl.ARRAY_BUFFER, data, gl.STATIC_DRAW);
        template.attributes[name].size = size;
    },
    
    // upload uniform data
    upload_uniform: function(name, data) {
        
        var ndim = template.uniforms[name].ndim;
        var size = template.uniforms[name].size;
        var vartype = template.uniforms[name].vartype;
        
        var float_suffix = {true: 'f', false: 'i'};
        var array_suffix = {true: 'v', false: ''};
            
        loc = template.uniforms[name].location;
        
        // scalar or vector uniform
        if (!(ndim instanceof Array)) {
            var funname = "uniform" + ndim + float_suffix[vartype == 'float'] + 
                array_suffix[size > 0];
            if (size > 0) {
                gl[funname](loc, size, data);
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
    },
    
    bind_buffer: function(name) {
        gl.bindBuffer(gl.ARRAY_BUFFER, template.attributes[name].buffer);
        gl.vertexAttribPointer(template.attributes[name].location,
                template.attributes[name].ndim, gl.FLOAT, false, 0, 0);
    },
};

// Compile a shader
// type is VERTEX_SHADER or FRAGMENT_SHADER
function compileShader(source, type) {
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
function initShaders() {

    vertexSource = template.vertex_shader;
    fragmentSource = template.fragment_shader;

    vertexShader = compileShader(vertexSource, "VERTEX_SHADER");
    fragmentShader = compileShader(fragmentSource, "FRAGMENT_SHADER");

    shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vertexShader);
    gl.attachShader(shaderProgram, fragmentShader);
    gl.linkProgram(shaderProgram);

    if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS))
    {
        window.alert("Could not initialise shaders");
    }

    gl.useProgram(shaderProgram);
}

// Initialize the shader variables
function initVariables() {
    // initialize and load attributes
    for (name in template.attributes) {
        dataloader.init_attribute(name);
        dataloader.upload_attribute(name);
    }
    
    // initialize uniforms
    for (name in template.uniforms) {
        dataloader.init_uniform(name);
    }
}

// Render the scene
function drawScene() {
    gl.viewport(0, 0, gl.viewportWidth, gl.viewportHeight);
    gl.clear(gl.COLOR_BUFFER_BIT);

    // bind all attribute buffers
    for (name in template.attributes)
        dataloader.bind_buffer(name);
    
    // navigation
    dataloader.upload_uniform("translation", [nav.tx, nav.ty]);
    dataloader.upload_uniform("scale", [nav.sx, nav.sy]);
    
    // render stuff
    gl.drawArrays(gl[template.primitive_type], 0, dataholder.size);
}

