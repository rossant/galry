import numpy as np
import OpenGL.GL as gl
from tools import enum

__all__ = ['PrimitiveType', 'GL_PRIMITIVE_TYPE_CONVERTER']

# Enumeration with the possible primitive types. They exactly correspond
# to their OpenGL counterparts.
PrimitiveType = enum("Points",  # one pixel per vertex
                     "Lines",  # one single line for two vertices
                     "LineStrip",  # consecutive line segments
                     "LineLoop",  # like line strip but closed
                     "Triangles",  # one triangle per triplet of vertices
                     "TriangleStrip",  # consecutive triangles
                     "TriangleFan",  # triangles all sharing the first vertex
                     )

# Primitive type converter.
GL_PRIMITIVE_TYPE_CONVERTER = {
    PrimitiveType.Points: gl.GL_POINTS,
    PrimitiveType.Lines: gl.GL_LINES,
    PrimitiveType.LineStrip: gl.GL_LINE_STRIP,
    PrimitiveType.LineLoop: gl.GL_LINE_LOOP,
    PrimitiveType.Triangles: gl.GL_TRIANGLES,
    PrimitiveType.TriangleStrip: gl.GL_TRIANGLE_STRIP,
    PrimitiveType.TriangleFan: gl.GL_TRIANGLE_FAN,
}
