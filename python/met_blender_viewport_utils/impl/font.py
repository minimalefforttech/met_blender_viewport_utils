# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
from __future__ import annotations
class _ext:
    """ External Dependencies """
    import logging
    import blf
    from met_viewport_utils.constants import  Align
    from met_viewport_utils.algorithm.color import parse_color
    from met_viewport_utils.shape.rect import Rect
    from met_viewport_utils.algorithm import types
    from met_viewport_utils.interfaces import IGPUFont
    
LOGGER = _ext.logging.getLogger("met_blender_viewport_utils.impl.font")

class GPUFont(_ext.IGPUFont):
    """ Convenience class for drawing text to screen
    
    Args:
        base(GPUFont): Optional base to start from
    
    Properties:
        id(int): readonly, the active font id
        path(Path): Path to font file
        
        family(str)
        weight(FontWeight)
        style(FontStyle)
        align(Align)
        path(Path)
        
        color(Vector)
        shadow_color(Vector)
        shadow_offset(Vector)
        shadow_blur(int)
        point_size(int)
        angle(float)
    """
    id:int = 0
    
    def copy(self)->GPUFont:
        copy = super().copy()
        copy.id = self.id
        return copy
            
    def _load_path(self):
        """ Load the font """
        self.id = _ext.blf.load(self.path.as_posix())
    
    def _preprocess(self, text:str, position:_ext.types.Vector2f, point_size:int, angle:float)->_ext.Rect:
        """ Preps the font and determins the bounds
        """
        # Todo
        # _ext.blf.disable(self.id, _ext.blf.CLIPPING)
        # _ext.blf.disable(self.id, _ext.blf.KERNING_DEFAULT)
        if angle == 0.0:
            _ext.blf.disable(self.id, _ext.blf.ROTATION)
        else:
            _ext.blf.enable(self.id, _ext.blf.ROTATION)
            _ext.blf.rotation(self.id, angle)
        
        if self.shadow_color is not None:
            _ext.blf.enable(self.id, _ext.blf.SHADOW)
            _ext.blf.shadow(self.id, self.shadow_blur, *_ext.parse_color(self.shadow_color))
            _ext.blf.shadow_offset(self.id, int(self.shadow_offset[0]), int(self.shadow_offset[1]))
        else:
            _ext.blf.disable(self.id, _ext.blf.SHADOW)
        
        _ext.blf.size(self.id, point_size)
        
        width, height = _ext.blf.dimensions(self.id, text)
        position = _ext.types.as_vector2f(position)
        if self.align & _ext.Align.Right:
            position[0] -= width
        elif self.align & _ext.Align.HCenter:
            position[0] -= width/2.0
        elif self.align & _ext.Align.Left:
            pass # default
        
        if self.align & _ext.Align.Top:
            position[1] -= height
        elif self.align & _ext.Align.VCenter:
            position[1] -= height/2.0
        elif self.align & _ext.Align.Bottom:
            pass # default
        
        _ext.blf.position(self.id, position[0], position[1], 0)
        return _ext.Rect(position, [width, height])
    
    def draw(self, text:str, position:_ext.types.Vector2f, point_size:int=None,
             angle:float=None, color:_ext.types.Vector2f=None)->_ext.Rect:
        """ Draw the font with optional overrides
        
        Args:
            text(str): text to draw
            position(Vector): 2d position to draw text
            point_size(int): optional point_size, defaults to self.point_size
            angle(float): optional angle, defaults to self.angle
            color(Vector): optional color, defaults to self.color
        
        Returns:
            Bounds of text just drawn
        """
        rect = self._preprocess(
            text,
            position,
            point_size if point_size is not None else self.point_size,
            angle if angle is not None else self.angle
        )
        color = _ext.parse_color(color) if color is not None else self.color
        if len(color) == 3:
            # Specify alpha
            _ext.blf.color(self.id, *color, 1.0)
        else:
            _ext.blf.color(self.id, *color)
        _ext.blf.draw(self.id, text)
        return rect
    
    def bounds(self, text:str, position:_ext.types.Vector2f, point_size:int=None,
               angle:float=None)->_ext.Rect:
        """ Get the bounding box of this text without drawing it
        
        Args:
            text(str): text to draw
            position(Vector): 2d position to draw text
            point_size(int): optional point_size, defaults to self.point_size
            angle(float): optional angle, defaults to self.angle
        
        Returns:
            Bounds
        """
        return self._preprocess(
            text,
            position,
            point_size if point_size is not None else self.point_size,
            angle if angle is not None else self.angle
        )
    