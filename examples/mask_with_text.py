# copyright (c) 2024 Alex Telford, http://minimaleffort.tech
# pylint: disable=fixme, import-error
from __future__ import annotations
import bpy
import numpy as np
from met_viewport_utils.constants import (
    Axis, Align, MouseButton, KeyboardModifier, FontWeight,
    GPUShaderPrimitiveType, GPUShaderState, FontStyle, ItemState, InteractionFlags)
from met_viewport_utils.shape.rect import Rect
from met_viewport_utils.shape.margins import Margins
from met_viewport_utils.shape.generate import border2d, square2d, arrow2d
from met_viewport_utils.algorithm.color import parse_color
from met_viewport_utils.items.hud_item import HudItem
from met_viewport_utils.items.font_item import FontItem

from met_blender_viewport_utils.impl.font import GPUFont
from met_blender_viewport_utils.impl.viewport import BlenderViewport
from met_blender_viewport_utils.impl.shaders import UniformColorShader

    
DEFAULT_FONT = GPUFont.from_props("Arial", weight=FontWeight.Normal)
DEFAULT_FONT.point_size = 16
DEFAULT_FONT.align = Align.Center
DEFAULT_FONT.color = "#FFFFFF"
DEFAULT_FONT.shadow_color = "#000000"



class HudMaskItem(HudItem):
    def __init__(self):
        super().__init__()
        self.flags |= InteractionFlags.Draggable
        self._shader = UniformColorShader()
        self._color = parse_color("#000000", alpha=0.5)
        self._shader.set_uniform("color", self._color)
        self._shader.primitive_type = GPUShaderPrimitiveType.Tris
        
        self._shader.state = GPUShaderState.UseAlpha
        self._handle:Align = None
        self._handle_drag_start = np.array([0, 0])
        self._drag_margins = Margins()
        
        self._handle_shader = UniformColorShader()
        self._handle_shader.set_uniform("color", [1.0, 1.0, 1.0, 0.3])
        self._handle_shader.primitive_type = GPUShaderPrimitiveType.Tris
        self._handle_shader.state = GPUShaderState.UseAlpha
        
        self._edge_default_color = [1.0, 1.0, 1.0, 0.3]
        self._edge_active_color = parse_color("#1E90FF", alpha=0.5)
        self._edge_shader = UniformColorShader()
        self._edge_shader.set_uniform("color", self._edge_default_color)
        self._edge_shader.primitive_type = GPUShaderPrimitiveType.Tris
        self._edge_shader.state = GPUShaderState.UseAlpha
        
        self._font = DEFAULT_FONT.copy()
        self._font.point_size = 24
        self._font.align = Align.Center
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, color):
        self._color = parse_color(color)
        self._shader.set_uniform("color", self._color)
        
    def _get_drag_data(self):
        return Margins(*self.margins)

    def _drag_move(self,
                   viewport,
                   start_data,
                   delta,
                   modifier):
        if not self._handle:
            return None
        if self._handle & Align.Left:
            self.margins.left = start_data.left + delta[0]
            self.margins.right = start_data.right + delta[0]
        if self._handle & Align.Top:
            self.margins.top = start_data.top - delta[1]
            self.margins.bottom = start_data.bottom - delta[1]
        if self._handle & Align.Right:
            self.margins.right = start_data.right - delta[0]
            self.margins.left = start_data.left - delta[0]
        if self._handle & Align.Bottom:
            self.margins.bottom = start_data.bottom + delta[1]
            self.margins.top = start_data.top + delta[1]
     
    def screen_rect(self, viewport:BlenderViewport)->Rect:
        return Rect(self.position, self.size)
    
    def _is_under_mouse(self, viewport, local_position, screen_position)->bool:
        outline = self.screen_rect(viewport).adjusted(self.margins)
        # Give 10px selection radius
        inner = outline.adjusted(Margins(5, 5, 5, 5))
        if inner.contains(screen_position):
            return False
        outer = outline.adjusted(Margins(-5, -5, -5, -5))
        return outer.contains(screen_position)
    
    def draw(self, viewport):
        # TODO: Compute points if viewport and margins are different
        rect = self.screen_rect(viewport)
        mesh = border2d(rect, self.margins)
        self._shader.draw({"pos": mesh.points}, indices=mesh.indices)
        
        if self._handle is not None:
            inner_rect = rect.adjusted(self.margins)
            box_width = 6
            if self._handle == Align.Left:
                box = Rect((inner_rect.left()-box_width/2, inner_rect.bottom()),
                           (box_width, inner_rect.height))
            elif self._handle == Align.Right:
                box = Rect((inner_rect.right()-box_width/2, inner_rect.bottom()),
                           (box_width, inner_rect.height))
            elif self._handle == Align.Bottom:
                box = Rect((inner_rect.left(), inner_rect.bottom()-box_width/2),
                           (inner_rect.width, box_width))
            elif self._handle == Align.Top:
                box = Rect((inner_rect.left(), inner_rect.top()-box_width/2),
                           (inner_rect.width, box_width))
            else:
                return
            
            if self.state & ItemState.Dragging:
                self._handle_shader.set_uniform("color", self._edge_active_color)
            else:
                self._handle_shader.set_uniform("color", self._edge_default_color)
            mesh = square2d(box)
            self._handle_shader.draw({"pos": mesh.points}, indices=mesh.indices)
            
            if self.state & ItemState.Dragging:
                center = inner_rect.center()
                aspect = inner_rect.width / inner_rect.height
                aspect_rect = self._font.draw(f"Aspect: {aspect:.2f}", center)
                self._font.draw(f"Margins: {self.margins.left:.0f}, {self.margins.top:.0f}, {self.margins.right:.0f}, {self.margins.bottom:.0f}",
                                center - np.array((0, aspect_rect.height + 5), dtype=np.float32))
            
            axis = self._handle
            if axis & (Align.Top|Align.Bottom):
                axis |= Align.HCenter
            else:
                axis |= Align.VCenter
            
            handle_position = inner_rect.point_at(axis)
                
            arrow_size = np.array((50, 50), dtype=np.float32)
            box = Rect(handle_position, arrow_size, Align.Center)
            arrow = arrow2d(box, heads=2)
            if self._handle & (Align.Top|Align.Bottom):
                arrow.rotate_by(90.0)
                
            self._handle_shader.draw({"pos": arrow.points}, indices=arrow.indices)
    
    def mouse_moved(self,
                    viewport,
                    local_position,
                    screen_position,
                    modifier):
        result = super().mouse_moved(viewport, local_position, screen_position, modifier)
        if self.state & ItemState.Dragging:
            return result
        outline = self.screen_rect(viewport).adjusted(self.margins)
        left_bound = Rect(outline.bottom_left(), [10, outline.height], Align.BottomCenter)
        if left_bound.contains(screen_position):
            self._handle = Align.Left
            return True
        
        right_bound = Rect(outline.bottom_right(), [10, outline.height], Align.BottomCenter)
        if right_bound.contains(screen_position):
            self._handle = Align.Right
            return True
        
        top_bound = Rect(outline.top_left(), [outline.width, 10], Align.LeftCenter)
        if top_bound.contains(screen_position):
            self._handle = Align.Top
            return True
        
        bottom_bound = Rect(outline.bottom_left(), [outline.width, 10], Align.LeftCenter)
        if bottom_bound.contains(screen_position):
            self._handle = Align.Bottom
            return True
        
        self._handle = None
        return result
        
    
        

class HudOverlayOperator(bpy.types.Operator):
    """Hud Overlay"""
    bl_idname = "view3d.hud_overlay"
    bl_label = "HUD Overlay"
    _handle = None
    _root = None
    
    @classmethod
    def _RemoveHandler(cls):
        if cls._handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(cls._handle, 'WINDOW')
            cls._handle = None

    def modal(self, context:bpy.types.Context, event:bpy.types.Event):
        is_hud_interaction = False
        if context.area.type == 'VIEW_3D':
            viewport = BlenderViewport(context)
            context.area.tag_redraw()
            context.view_layer.update()
            modifier = KeyboardModifier.NoKeyboardModifier
            if event.ctrl:
                modifier |= KeyboardModifier.Ctrl
            if event.shift:
                modifier |= KeyboardModifier.Shift
            if event.alt:
                modifier |= KeyboardModifier.Alt

            if event.type == 'MOUSEMOVE':
                mouse_pos = np.array([event.mouse_region_x, event.mouse_region_y], dtype=np.float32)
                self._root.mouse_moved(viewport, mouse_pos, mouse_pos, modifier)
                    
            elif event.type == 'LEFTMOUSE':
                mouse_pos = np.array([event.mouse_region_x, event.mouse_region_y], dtype=np.float32)
                if event.value == "PRESS":
                    # TODO: right clicks
                    is_hud_interaction = self._root.mouse_pressed(viewport, mouse_pos, mouse_pos, MouseButton.Left, modifier)
                else:  # release
                    is_hud_interaction = self._root.mouse_released(viewport, mouse_pos, mouse_pos, MouseButton.Left, modifier)

            elif event.type in {'ESC'}:
                self._RemoveHandler()
                return {'CANCELLED'}
        
        return {'RUNNING_MODAL'} if is_hud_interaction else {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            self._root = HudMaskItem()
            self._root.margins = Margins(100, 50, 100, 50)
            item = FontItem("{scene.frame_current}", DEFAULT_FONT)
            item.data["scene"] = context.scene
            item.align = Align.BottomCenter
            item.font.align = Align.TopCenter
            item.parent = self._root
            item = FontItem("SampleProject", DEFAULT_FONT)
            item.flags = InteractionFlags.Draggable
            item.align = Align.BottomLeft
            item.font.align = Align.TopLeft
            item.parent = self._root
            item = FontItem("{camera.lens:.2f}mm", DEFAULT_FONT)
            item.data["camera"] = bpy.data.cameras["Camera"]
            item.align = Align.BottomRight
            item.font.align = Align.TopRight
            item.parent = self._root
            
            item = FontItem("This text can move", DEFAULT_FONT)
            item.font.color = parse_color("#1E90FF")
            item.font.point_size = 24
            item.font.weight = FontWeight.Bold
            item.font.style = FontStyle.Italic
            item.align = Align.TopLeft
            item.flags = InteractionFlags.Draggable
            item.parent = self._root
            
            self.__class__._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.__class__.draw, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}
    

    def draw(self, context:bpy.types.Context):
        if context.area.type == 'VIEW_3D':
            viewport = BlenderViewport(context)
            self._root.size = viewport.rect().size
            self._root.draw(viewport)
            for item in self._root.iter_descendants(HudItem):
                if item.state & ItemState.Visible:
                    item.draw(viewport)

def register():
    bpy.utils.register_class(HudOverlayOperator)


def unregister():
    bpy.utils.unregister_class(HudOverlayOperator)

if __name__ == "__main__":
    register()
