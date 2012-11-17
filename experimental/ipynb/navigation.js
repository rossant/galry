
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