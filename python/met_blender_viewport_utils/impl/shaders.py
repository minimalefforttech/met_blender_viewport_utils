# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
"""Built in shaders
"""
class _ext:
    """ External Dependencies """
    from .shader import GPUShader
    from met_viewport_utils.constants import (
        GPUShaderUniformType,
        GPUShaderPrimitiveType
    )
    import gpu

class FlatColorShader(_ext.GPUShader):
    """
    Take a 3D position and color for each vertex without color interpolation.
    
    Args:
        polyline(bool): If true use the polyline shader
    
    ShaderParams:
        color: in vec4
        pos: in vec3
    """
    def __init__(self, polyline:bool=False):
        if polyline:
            shader = _ext.gpu.shader.from_builtin('POLYLINE_FLAT_COLOR')
        else:
            shader = _ext.gpu.shader.from_builtin('FLAT_COLOR')
        super().__init__(shader)


class VertexColorShader(_ext.GPUShader):
    """
    Take a 3D position and color for each vertex with perspective correct interpolation.
    
    Args:
        polyline(bool): If true use the polyline shader
    
    ShaderParams:
        color: in vec4
        pos: in vec3
    """
    def __init__(self, polyline:bool=False):
        if polyline:
            shader = _ext.gpu.shader.from_builtin('POLYLINE_SMOOTH_COLOR')
        else:
            shader = _ext.gpu.shader.from_builtin('SMOOTH_COLOR')
        super().__init__(shader)


class UniformColorShader(_ext.GPUShader):
    """
    Take a single color for all the vertices and a 3D position for each vertex.
    
    Args:
        polyline(bool): If true use the polyline shader
    
    ShaderParams:
        color: uniform vec4
        pos: in vec3
    """
    def __init__(self, polyline:bool=False):
        if polyline:
            shader = _ext.gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
        else:
            shader = _ext.gpu.shader.from_builtin('UNIFORM_COLOR')
        super().__init__(shader)
        self._uniform_types["color"] = _ext.GPUShaderUniformType.Float
        
        
class ImageShader(_ext.GPUShader):
    """
    Draw a texture in 3D. Take a 3D position and a 2D texture coordinate for each vertex.
    
    ShaderParams:
        image: uniform sampler2D
        texCoord: in vec2
        pos: in vec3
    """
    primitive_type = _ext.GPUShaderPrimitiveType.Tris
    def __init__(self):
        shader = _ext.gpu.shader.from_builtin('IMAGE')
        super().__init__(shader)
        self._uniform_types["sampler2D"] = _ext.GPUShaderUniformType.Sampler
        
        
class ImageUniformColorShader(_ext.GPUShader):
    """
    Take a 3D position and color for each vertex with linear interpolation in window space.
    
    ShaderParams:
        color: uniform vec4
        image: uniform sampler2D
        texCoord: in vec2
        pos: in vec3
    """
    primitive_type = _ext.GPUShaderPrimitiveType.Tris
    def __init__(self):
        shader = _ext.gpu.shader.from_builtin('IMAGE_COLOR')
        super().__init__(shader)
        self._uniform_types["color"] = _ext.GPUShaderUniformType.Float
        self._uniform_types["sampler2D"] = _ext.GPUShaderUniformType.Sampler
