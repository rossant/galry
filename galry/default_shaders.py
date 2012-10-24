__all__ = ['DEFAULT_SHADERS']

# default shaders
DEFAULT_SHADERS = dict(
# Position-only
# -------------
    position={
        "vertex": """
%AUTODECLARATIONS%

void main()
{
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position;
    gl_FrontColor = gl_Color;
}
        """,
        
        "fragment": """
void main()
{
    gl_FragColor = gl_Color;
}
        """
    },
    
# Position and color
# ------------------
    position_color={
        "vertex": """
%AUTODECLARATIONS%

void main()
{
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position; 
    gl_FrontColor = color;
}
        """,
        
        "fragment": """
void main()
{
    gl_FragColor = gl_Color;
}
        """
    },

# Textured rectangle
# ------------------
    textured_rectangle = {
        "vertex": """
%AUTODECLARATIONS%

void main()
{
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position;
    gl_FrontColor = gl_Color;
    
    gl_TexCoord[0] = texture_coordinates;
}
        """,
        
        "fragment": """
uniform sampler2D tex_sampler0;

void main()
{
    gl_FragColor = texture2D(tex_sampler0, gl_TexCoord[0].st);
}
        """
    },
    
# Sprites
# -------
    sprites={
    "vertex": """
%AUTODECLARATIONS%

void main()
{
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position;
    gl_FrontColor = gl_Color;
    
    gl_PointSize = point_size;
}
""",

    "fragment": """
uniform sampler2D tex_sampler0;

void main()
{
    gl_FragColor = texture2D(tex_sampler0, gl_PointCoord) * gl_Color;
}
"""},

# Colored sprites
# ---------------
    sprites_color={
    "vertex": """
%AUTODECLARATIONS%

void main()
{
    if (!is_static)
        gl_Position = gl_ModelViewProjectionMatrix * position;
    else
        gl_Position = position;
    gl_FrontColor = color;
    
    gl_PointSize = point_size;
}
""",

    "fragment": """
uniform sampler2D tex_sampler0;

void main()
{
    gl_FragColor = texture2D(tex_sampler0, gl_PointCoord) * gl_Color;
}
"""},
)
