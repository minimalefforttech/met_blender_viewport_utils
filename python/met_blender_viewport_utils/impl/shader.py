# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
class _ext:
    """ External Dependencies """
    import gpu
    import bpy
    import typing
    import numpy as np
    from gpu_extras.batch import batch_for_shader
    from met_viewport_utils.constants import (
        GPUShaderPrimitiveType,
        GPUShaderUniformType,
        GPUShaderState)
    from .state import GPURestoreState
    from met_viewport_utils.interfaces import IGPUShader


class GPUShader(_ext.IGPUShader):
    """ Simple wrapper around a blender GPU shader draw
    
    Args:
        shader(GPUShader): Shader to draw
    
    Properties:
        shader(GPUShader): Internal shader
        primitive(GPUShaderPrimitiveType): primitive drawing type
        state(GPUShaderState): Optional state to set while drawing this shader
        size(float): Width of points or lines
    """
    # Set the typing on the root
    shader:_ext.gpu.types.GPUShader = None  # Internal shader pointer

    def __init__(self, shader:_ext.gpu.types.GPUShader):
        super().__init__(shader)
        self._last_batch = None
        
    
    def _batch(self,
               vertex_in:_ext.typing.Dict[str, _ext.typing.Any],
               primitive_type:_ext.GPUShaderPrimitiveType,
               indices:_ext.typing.Optional[_ext.typing.List[int]]=None)->_ext.gpu.types.GPUBatch:
        """Batch the shader for processing

        Args:
            vertex_in (Dict[str, Any]): vertex shader inputs
            primitive_type (GPUShaderPrimitiveType): primitive type to draw
            indices (List[int], optional): Optional indices to pass for mapping inputs

        Returns:
            gpu.types.GPUBatch
        """

        if not self._last_batch:
            batch = _ext.batch_for_shader(self.shader, primitive_type.value, vertex_in, indices=indices)
            self._last_batch = [batch, primitive_type, vertex_in, indices]
            return batch

        last_batch, last_primitive, last_vertex_in, last_indices = self._last_batch
        try:
            # There may be numpy arrays, this is a lazy equality operator
            _ext.np.testing.assert_equal(vertex_in, last_vertex_in)
            _ext.np.testing.assert_equal(indices, last_indices)
        except AssertionError:
            pass
        else:
            if primitive_type == last_primitive:
                return last_batch

        batch = _ext.batch_for_shader(self.shader, primitive_type.value, vertex_in, indices=indices)
        self._last_batch = [batch, primitive_type, vertex_in, indices]
        return batch
    
    def _set_uniform_by_type(self, name:str, value):
        if isinstance(value, _ext.gpu.types.GPUTexture):
            self._uniform_types[name] = _ext.GPUShaderUniformType.Sampler
            self.shader.uniform_sampler(name, value)
        else:
            super()._set_uniform_by_type(name, value)
    
    def draw(self,
             vertex_in:_ext.typing.Dict[str, _ext.typing.Any],
             primitive_type:_ext.GPUShaderPrimitiveType=None,
             indices:_ext.typing.Optional[_ext.typing.List[int]]=None,
             size:_ext.typing.Optional[float]=None,
             state:_ext.typing.Optional[_ext.GPUShaderState]=None,
             **kwargs):
        """Draw this shader

        Args:
            vertex_in (Dict[str, Any]): Inputs to vertex shader
            primitive_type (GPUShaderPrimitiveType, optional): Primitive override
            indices (List[int], optional): indices map, optional
            size (float, optional): size override
            state (GPUShaderState, optional): state override
        """
        if state is None:
            state = self.state
        if size is None:
            size = self.size
        if size:
            _ext.gpu.state.line_width_set(size)
            _ext.gpu.state.point_size_set(size)
        primitive_type = primitive_type or self.primitive_type
        batch = self._batch(vertex_in, primitive_type, indices)
        self._prep_shader()
        for key, value in kwargs.items():
            self.set_uniform(key, value)
        with _ext.GPURestoreState(state):
            batch.draw(self.shader)