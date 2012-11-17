
function get_pos(e) {
    return [2 * e.pageX / width - 1, -(2 * e.pageY / height - 1)];
}

// Return the inf norm between two points.
function get_maximum_norm(p1, p2) {
    return Math.max(Math.abs(p1[0]-p2[0]), Math.abs(p1[1]-p2[1]));
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
        
        //debug(gen.action + " " + gen.key + " " + gen.key_modifier);
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


