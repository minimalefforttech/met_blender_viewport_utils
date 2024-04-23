# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
class _ext:
    """ External Dependencies """
    from met_viewport_utils.constants import GPUShaderState
    from met_viewport_utils.interfaces import IGPURestoreState
    import gpu


class GPURestoreState(_ext.IGPURestoreState):
    """Context manager to temporarily set and restore state while drawing

    Args:
        flags (GpuShaderState): State flags to set
    
    Usage:
        with GpuRestoreState(GpuShaderState.Alpha|GpuShaderState.Depth):
            batch.draw()
    """
    def _get_state(cls, state:_ext.GPUShaderState):
        if state == _ext.GPUShaderState.UseAlpha:
            return _ext.gpu.state.blend_get()
        elif state == _ext.GPUShaderState.UseDepth:
            return (_ext.gpu.state.depth_test_get(), _ext.gpu.state.depth_mask_get())
    
    def _set_state(cls, state:_ext.GPUShaderState, param):
        if state == _ext.GPUShaderState.UseAlpha:
            _ext.gpu.state.blend_set(param)
        elif state == _ext.GPUShaderState.UseDepth:
            depth_test, depth_mask = param
            _ext.gpu.state.depth_test_set(depth_test)
            _ext.gpu.state.depth_mask_set(depth_mask)
