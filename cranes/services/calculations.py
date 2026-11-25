"""
Geometric calculations, scaling, and coordinate mapping for crane 2D front-elevation SVG.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any


@dataclass
class DrawingLayout:
    # Canvas properties
    canvas_width: float
    canvas_height: float
    scale: float

    # Real dimensions in mm
    span_mm: float
    girder_depth_mm: float
    end_carriage_height_mm: float
    end_carriage_width_mm: float
    trolley_width_mm: float
    trolley_height_mm: float
    hook_block_height_mm: float
    hook_block_width_mm: float
    runway_rail_height_mm: float
    runway_rail_width_mm: float
    lifting_height_mm: float
    capacity_t: float

    # Scaled pixel dimensions
    span_px: float
    girder_depth_px: float
    end_carriage_height_px: float
    end_carriage_width_px: float
    trolley_width_px: float
    trolley_height_px: float
    hook_block_height_px: float
    hook_block_width_px: float
    runway_rail_height_px: float
    runway_rail_width_px: float
    lifting_height_px: float

    # Key coordinate reference points (origin top-left)
    rail_top_y: float
    left_rail_center_x: float
    right_rail_center_x: float
    girder_top_y: float
    girder_bottom_y: float
    girder_left_x: float
    girder_right_x: float
    trolley_center_x: float
    trolley_top_y: float
    hook_top_y: float
    hook_bottom_y: float
    lowest_hook_y: float


def compute_drawing_layout(params: Dict[str, Any], canvas_width: float = 1600.0, canvas_height: float = 1000.0) -> DrawingLayout:
    """
    Computes real-world to SVG coordinate mapping with uniform aspect-ratio scaling.
    """
    span = float(params['span'])
    girder_depth = float(params['girder_depth'])
    end_carriage_height = float(params['end_carriage_height'])
    trolley_width = float(params['trolley_width'])
    hook_block_height = float(params['hook_block_height'])
    runway_rail_height = float(params['runway_rail_height'])
    lifting_height = float(params['lifting_height'])
    capacity = float(params['capacity'])

    # Visual derived dimensions (clearly documented proportional assumptions)
    # End carriage width in front elevation (profile width across rail head)
    end_carriage_width = max(350.0, min(800.0, span * 0.035))
    # Rail width typically 0.8x to 1.2x rail height
    runway_rail_width = max(80.0, runway_rail_height * 1.1)
    # Trolley height proportional to width and girder
    trolley_height = max(400.0, min(1200.0, girder_depth * 0.65))
    # Hook block width
    hook_block_width = max(250.0, hook_block_height * 0.6)

    # Calculate total bounding box in real-world mm:
    # Horizontal: Span + End Carriage extensions + Margins for dimension lines
    total_horizontal_mm = span + (end_carriage_width * 2) + 1200.0
    # Vertical: Rail height + End carriage/Girder + Lifting height envelope
    total_vertical_mm = runway_rail_height + girder_depth + end_carriage_height + min(lifting_height, 6000.0) + 1800.0

    # Available drawing area inside canvas (accounting for title block and outer margins)
    margin_x = 140.0
    margin_top = 130.0
    margin_bottom = 220.0  # Room for title block and bottom dimensions
    avail_width = canvas_width - (2 * margin_x)
    avail_height = canvas_height - (margin_top + margin_bottom)

    scale_x = avail_width / total_horizontal_mm
    scale_y = avail_height / total_vertical_mm
    scale = min(scale_x, scale_y)

    # Scaled dimensions in pixels
    span_px = span * scale
    girder_depth_px = girder_depth * scale
    end_carriage_height_px = end_carriage_height * scale
    end_carriage_width_px = end_carriage_width * scale
    trolley_width_px = trolley_width * scale
    trolley_height_px = trolley_height * scale
    hook_block_height_px = hook_block_height * scale
    hook_block_width_px = hook_block_width * scale
    runway_rail_height_px = runway_rail_height * scale
    runway_rail_width_px = runway_rail_width * scale
    
    # We cap the visual wire rope drop for lifting height display so drawings fit elegantly
    visual_lift_mm = min(lifting_height, 5500.0)
    lifting_height_px = visual_lift_mm * scale

    # Centering calculations
    center_x = canvas_width / 2.0
    left_rail_center_x = center_x - (span_px / 2.0)
    right_rail_center_x = center_x + (span_px / 2.0)

    # Reference rail top level
    rail_top_y = margin_top + 160.0
    
    # Girder sits between / on end carriages
    girder_top_y = rail_top_y - (end_carriage_height_px * 0.3)
    girder_bottom_y = girder_top_y + girder_depth_px
    girder_left_x = left_rail_center_x + (end_carriage_width_px * 0.1)
    girder_right_x = right_rail_center_x - (end_carriage_width_px * 0.1)

    # Trolley centered on span by default
    trolley_center_x = center_x
    trolley_top_y = girder_bottom_y + 10.0  # Underslung hoist configuration
    
    # Hook block
    rope_drop_px = max(60.0, lifting_height_px * 0.35)
    hook_top_y = trolley_top_y + trolley_height_px + rope_drop_px
    hook_bottom_y = hook_top_y + hook_block_height_px
    lowest_hook_y = hook_top_y + lifting_height_px

    return DrawingLayout(
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        scale=scale,
        span_mm=span,
        girder_depth_mm=girder_depth,
        end_carriage_height_mm=end_carriage_height,
        end_carriage_width_mm=end_carriage_width,
        trolley_width_mm=trolley_width,
        trolley_height_mm=trolley_height,
        hook_block_height_mm=hook_block_height,
        hook_block_width_mm=hook_block_width,
        runway_rail_height_mm=runway_rail_height,
        runway_rail_width_mm=runway_rail_width,
        lifting_height_mm=lifting_height,
        capacity_t=capacity,
        span_px=span_px,
        girder_depth_px=girder_depth_px,
        end_carriage_height_px=end_carriage_height_px,
        end_carriage_width_px=end_carriage_width_px,
        trolley_width_px=trolley_width_px,
        trolley_height_px=trolley_height_px,
        hook_block_height_px=hook_block_height_px,
        hook_block_width_px=hook_block_width_px,
        runway_rail_height_px=runway_rail_height_px,
        runway_rail_width_px=runway_rail_width_px,
        lifting_height_px=lifting_height_px,
        rail_top_y=rail_top_y,
        left_rail_center_x=left_rail_center_x,
        right_rail_center_x=right_rail_center_x,
        girder_top_y=girder_top_y,
        girder_bottom_y=girder_bottom_y,
        girder_left_x=girder_left_x,
        girder_right_x=girder_right_x,
        trolley_center_x=trolley_center_x,
        trolley_top_y=trolley_top_y,
        hook_top_y=hook_top_y,
        hook_bottom_y=hook_bottom_y,
        lowest_hook_y=lowest_hook_y,
    )
