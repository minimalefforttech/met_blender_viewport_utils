# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
class _ext:
    """ External Dependencies """
    import typing
    import bpy
    from bpy_extras import view3d_utils
    import gpu
    from met_viewport_utils.interfaces import IViewport
    from met_viewport_utils.shape.rect import Rect
    from met_viewport_utils.algorithm import types
    from mathutils import Vector

class BlenderViewport(_ext.IViewport):
    def __init__(self, context:_ext.bpy.types.Context):
        self._context = context

    def rect(self)->_ext.Rect:
        """Viewport rect, note that this may sometimes be the window rect depending on what context is passed
        If things are not snapping correctly, confirm this is the correct rect

        Returns:
            Rect
        """
        x, y, width, height = _ext.gpu.state.viewport_get()
        return _ext.Rect([x, y], [width, height])
    
    def screen_to_world(self, screen_position:_ext.types.Vector2fCompat, depth_point:_ext.types.Vector3f)->_ext.types.Vector3f:
        """From a position in the screen, return a tuple representing the ray origin and direction

        Args:
            screen_position (Vector2f): screen position
            depth_point(Vector3f): position in space to match

        Returns:
            Vector3f position
        """
        screen_position = _ext.types.as_vector2f(screen_position)
        depth_point = _ext.types.as_vector3f(depth_point)
        region = self._context.region
        region3D = self._context.space_data.region_3d
        view_location = _ext.view3d_utils.region_2d_to_location_3d(
            region, region3D, _ext.screen_position(screen_position), _ext.Vector(depth_point))
        return _ext.types.as_vector3f(view_location)
    
    def screen_to_ray(self, screen_position:_ext.types.Vector2fCompat)->_ext.typing.Tuple[_ext.types.Vector3f]:
        """From a position in the screen, return a tuple representing the ray origin and direction

        Args:
            screen_position (Vector2f): screen position

        Returns:
            Vector3f origin, ray_dir
        """
        screen_position = _ext.types.as_vector2f(screen_position)
        region = self._context.region
        region3D = self._context.space_data.region_3d
        origin = _ext.view3d_utils.region_2d_to_origin_3d(region, region3D, _ext.Vector(screen_position))
        ray = _ext.view3d_utils.region_2d_to_vector_3d(region, region3D, _ext.Vector(screen_position))
        return (origin, ray)
    
    def world_to_screen(self, world_position:_ext.types.Vector3fCompat)->_ext.types.Vector2f:
        """From a position in the screen, return a tuple representing the ray origin and direction

        Args:
            world_position (Vector2f): screen position

        Returns:
            Vector2d screen_position
        """
        world_position = _ext.types.as_vector3f(world_position)
        region = self._context.region
        region3D = self._context.space_data.region_3d
        point = _ext.Vector(world_position)
        view_location = _ext.view3d_utils.location_3d_to_region_2d(region, region3D, point)
        return _ext.types.as_vector2f(view_location)
