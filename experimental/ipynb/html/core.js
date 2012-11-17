

// Main function
function webGLStart() {
    debugObj = $('#debug');
    var canvas = document.getElementById("canvas");
    // Disable right click context menu on the canvas.
    canvas.oncontextmenu = function() {return false;};
    
    $('canvas').attr('width', width);
    $('canvas').attr('height', height);
    
    // make bindings
    $('canvas').mousedown(gen.mousedown);
    $('canvas').dblclick(gen.dblclick);
    $('canvas').mouseup(gen.mouseup);
    $('canvas').mousemove(gen.mousemove);
    $('canvas').mousewheel(gen.mousewheel);
    $('canvas').keydown(gen.keydown);
    $('canvas').keyup(gen.keyup);
    $('canvas').focusout(gen.focusout);        
        
    // allow to move the mouse outside the canvas
    $(document).mousemove(gen.mousemove);
    $(document).mouseup(gen.mouseup);
        
    // Initialize everything
    initGL(canvas);
    initShaders(VS, FS);
    initVariables();

    // Background color
    gl.clearColor(0.0, 0.0, 0.0, 1.0);
    
    // Render everything
    drawScene();
}