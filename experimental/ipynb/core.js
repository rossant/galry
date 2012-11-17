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




