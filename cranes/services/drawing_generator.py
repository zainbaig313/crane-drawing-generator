"""
Pure Python 2D Parametric Drawing Generator for Single-Girder Overhead Travelling Cranes.
Generates clean, dimensioned, responsive engineering-standard SVG markup.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from .calculations import compute_drawing_layout, DrawingLayout
from .validation import validate_crane_parameters


class CraneDrawingGenerator:
    """
    Parametric SVG drawing engine for single-girder overhead cranes.
    """

    def __init__(self, params: Dict[str, Any], design_name: str = "Parametric Crane Design"):
        # Validate parameters before drawing
        cleaned, errors = validate_crane_parameters(params)
        if errors:
            first_err = next(iter(errors.values()))[0]
            raise ValueError(f"Invalid crane parameters for drawing generation: {first_err}")
        self.params = cleaned
        self.design_name = design_name
        self.layout: DrawingLayout = compute_drawing_layout(cleaned)

    def generate_svg(self) -> str:
        """
        Assembles all SVG elements into a complete, standalone, valid XML SVG string.
        """
        lo = self.layout
        
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lo.canvas_width:.0f} {lo.canvas_height:.0f}" '
            f'width="100%" height="100%" preserveAspectRatio="xMidYMid meet" class="crane-drawing-svg">',
            self._render_defs(),
            self._render_background_and_grid(),
            self._render_runway_rails(),
            self._render_end_carriages(),
            self._render_main_girder(),
            self._render_hoist_and_trolley(),
            self._render_hook_block(),
            self._render_reference_lines(),
            self._render_dimension_annotations(),
            self._render_title_block(),
            '</svg>'
        ]
        return "\n".join(svg_parts)

    def _render_defs(self) -> str:
        return """
    <defs>
        <!-- Engineering arrowhead markers -->
        <marker id="arrow-start" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 10 1 L 0 5 L 10 9 z" fill="#0f172a" />
        </marker>
        <marker id="arrow-end" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#0f172a" />
        </marker>
        <!-- Subtle drafting grid pattern -->
        <pattern id="drafting-grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f1f5f9" stroke-width="1" />
        </pattern>
        <!-- Hatching for building runway beam stubs -->
        <pattern id="beam-hatch" width="8" height="8" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="8" stroke="#cbd5e1" stroke-width="1.5" />
        </pattern>
    </defs>
    """

    def _render_background_and_grid(self) -> str:
        lo = self.layout
        return f"""
    <!-- Canvas Background -->
    <rect width="{lo.canvas_width:.0f}" height="{lo.canvas_height:.0f}" fill="#ffffff" />
    <rect width="{lo.canvas_width:.0f}" height="{lo.canvas_height:.0f}" fill="url(#drafting-grid)" />
    <!-- Drawing Border -->
    <rect x="20" y="20" width="{lo.canvas_width - 40:.0f}" height="{lo.canvas_height - 40:.0f}" fill="none" stroke="#0f172a" stroke-width="2" />
    <rect x="25" y="25" width="{lo.canvas_width - 50:.0f}" height="{lo.canvas_height - 50:.0f}" fill="none" stroke="#64748b" stroke-width="0.75" />
    """

    def _render_runway_rails(self) -> str:
        lo = self.layout
        half_rw = lo.runway_rail_width_px / 2.0
        beam_h = 45.0
        beam_w = lo.runway_rail_width_px * 2.2

        svg = []
        # Left and Right Rail + Runway Girders
        for x_center, side in [(lo.left_rail_center_x, "left"), (lo.right_rail_center_x, "right")]:
            rail_x = x_center - half_rw
            rail_y = lo.rail_top_y
            beam_x = x_center - (beam_w / 2.0)
            beam_y = rail_y + lo.runway_rail_height_px

            # Runway Support Beam Stub (hatched)
            svg.append(f"""
            <!-- {side.title()} Runway Support Structure -->
            <rect x="{beam_x:.1f}" y="{beam_y:.1f}" width="{beam_w:.1f}" height="{beam_h:.1f}" fill="url(#beam-hatch)" stroke="#334155" stroke-width="1.5" />
            <line x1="{beam_x - 15:.1f}" y1="{beam_y + beam_h:.1f}" x2="{beam_x + beam_w + 15:.1f}" y2="{beam_y + beam_h:.1f}" stroke="#334155" stroke-width="2" />
            
            <!-- {side.title()} Crane Runway Rail -->
            <rect x="{rail_x:.1f}" y="{rail_y:.1f}" width="{lo.runway_rail_width_px:.1f}" height="{lo.runway_rail_height_px:.1f}" 
                  fill="#475569" stroke="#0f172a" stroke-width="1.5" rx="2" />
            <line x1="{x_center:.1f}" y1="{rail_y - 25:.1f}" x2="{x_center:.1f}" y2="{beam_y + beam_h + 15:.1f}" 
                  stroke="#94a3b8" stroke-width="1" stroke-dasharray="6,4" />
            """)
        return "".join(svg)

    def _render_end_carriages(self) -> str:
        lo = self.layout
        c_w = lo.end_carriage_width_px
        c_h = lo.end_carriage_height_px
        wheel_r = max(10.0, lo.runway_rail_height_px * 0.9)

        svg = []
        for x_center, side in [(lo.left_rail_center_x, "left"), (lo.right_rail_center_x, "right")]:
            c_x = x_center - (c_w / 2.0)
            c_y = lo.rail_top_y - c_h + wheel_r

            # Carriage Chassis
            svg.append(f"""
            <!-- {side.title()} End Carriage -->
            <g id="{side}-end-carriage">
                <!-- Main Carriage Body -->
                <rect x="{c_x:.1f}" y="{c_y:.1f}" width="{c_w:.1f}" height="{c_h:.1f}" fill="#334155" stroke="#0f172a" stroke-width="2" rx="3" />
                <!-- End Carriage Stiffener & Bumper -->
                <rect x="{c_x + 5:.1f}" y="{c_y + 5:.1f}" width="{c_w - 10:.1f}" height="{c_h - 10:.1f}" fill="#475569" stroke="#1e293b" stroke-width="1" />
                <!-- Wheels resting on rail -->
                <circle cx="{x_center - (c_w * 0.28):.1f}" cy="{lo.rail_top_y:.1f}" r="{wheel_r:.1f}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
                <circle cx="{x_center - (c_w * 0.28):.1f}" cy="{lo.rail_top_y:.1f}" r="{wheel_r * 0.4:.1f}" fill="#94a3b8" />
                <circle cx="{x_center + (c_w * 0.28):.1f}" cy="{lo.rail_top_y:.1f}" r="{wheel_r:.1f}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
                <circle cx="{x_center + (c_w * 0.28):.1f}" cy="{lo.rail_top_y:.1f}" r="{wheel_r * 0.4:.1f}" fill="#94a3b8" />
                <!-- Rail sweeper / Bumper stubs -->
                <rect x="{c_x - 8:.1f}" y="{lo.rail_top_y - (wheel_r * 0.8):.1f}" width="8" height="{wheel_r * 1.6:.1f}" fill="#0f172a" />
                <rect x="{c_x + c_w:.1f}" y="{lo.rail_top_y - (wheel_r * 0.8):.1f}" width="8" height="{wheel_r * 1.6:.1f}" fill="#0f172a" />
            </g>
            """)
        return "".join(svg)

    def _render_main_girder(self) -> str:
        lo = self.layout
        g_w = lo.girder_right_x - lo.girder_left_x
        g_h = lo.girder_depth_px
        g_x = lo.girder_left_x
        g_y = lo.girder_top_y

        # Stiffener plate spacing across span
        num_stiffeners = max(4, min(12, int(lo.span_mm // 2500)))
        stiffener_lines = []
        for i in range(1, num_stiffeners):
            sx = g_x + (g_w * (i / num_stiffeners))
            stiffener_lines.append(f'<line x1="{sx:.1f}" y1="{g_y + 4:.1f}" x2="{sx:.1f}" y2="{g_y + g_h - 4:.1f}" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="4,4" />')

        stiffeners_svg = "\n".join(stiffener_lines)

        return f"""
        <!-- Main Girder Assembly -->
        <g id="main-girder">
            <!-- Box Girder Outer Profile -->
            <rect x="{g_x:.1f}" y="{g_y:.1f}" width="{g_w:.1f}" height="{g_h:.1f}" fill="#f8fafc" stroke="#0f172a" stroke-width="2.5" />
            <!-- Top Flange Accent -->
            <rect x="{g_x:.1f}" y="{g_y:.1f}" width="{g_w:.1f}" height="{max(6.0, g_h * 0.06):.1f}" fill="#e2e8f0" stroke="#0f172a" stroke-width="1.5" />
            <!-- Bottom Flange (Trolley running track) -->
            <rect x="{g_x:.1f}" y="{g_y + g_h - max(8.0, g_h * 0.08):.1f}" width="{g_w:.1f}" height="{max(8.0, g_h * 0.08):.1f}" fill="#cbd5e1" stroke="#0f172a" stroke-width="1.5" />
            <!-- Internal diaphragm/stiffener reference lines -->
            {stiffeners_svg}
            <!-- End Joint Connection Gusset Plates -->
            <polygon points="{g_x:.1f},{g_y:.1f} {g_x + 35:.1f},{g_y:.1f} {g_x:.1f},{g_y + 45:.1f}" fill="#475569" stroke="#0f172a" stroke-width="1" />
            <polygon points="{g_x + g_w:.1f},{g_y:.1f} {g_x + g_w - 35:.1f},{g_y:.1f} {g_x + g_w:.1f},{g_y + 45:.1f}" fill="#475569" stroke="#0f172a" stroke-width="1" />
            <polygon points="{g_x:.1f},{g_y + g_h:.1f} {g_x + 35:.1f},{g_y + g_h:.1f} {g_x:.1f},{g_y + g_h - 45:.1f}" fill="#475569" stroke="#0f172a" stroke-width="1" />
            <polygon points="{g_x + g_w:.1f},{g_y + g_h:.1f} {g_x + g_w - 35:.1f},{g_y + g_h:.1f} {g_x + g_w:.1f},{g_y + g_h - 45:.1f}" fill="#475569" stroke="#0f172a" stroke-width="1" />
            <!-- Crane Label on Girder -->
            <text x="{lo.canvas_width / 2.0:.1f}" y="{g_y + (g_h / 2.0) + 5:.1f}" font-family="Arial, Helvetica, sans-serif" 
                  font-size="{max(12.0, min(24.0, g_h * 0.35)):.1f}" font-weight="bold" fill="#334155" text-anchor="middle" letter-spacing="3">
                SWL {lo.capacity_t:g} TONNES — SINGLE GIRDER CRANE
            </text>
        </g>
        """

    def _render_hoist_and_trolley(self) -> str:
        lo = self.layout
        tw = lo.trolley_width_px
        th = lo.trolley_height_px
        tx = lo.trolley_center_x - (tw / 2.0)
        ty = lo.trolley_top_y

        wheel_r = max(6.0, th * 0.12)
        bottom_flange_y = lo.girder_bottom_y

        return f"""
        <!-- Hoist / Trolley Assembly (Underslung) -->
        <g id="hoist-trolley">
            <!-- Trolley Guide Wheels on bottom flange -->
            <circle cx="{tx + (tw * 0.25):.1f}" cy="{bottom_flange_y - (wheel_r * 0.3):.1f}" r="{wheel_r:.1f}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
            <circle cx="{tx + (tw * 0.75):.1f}" cy="{bottom_flange_y - (wheel_r * 0.3):.1f}" r="{wheel_r:.1f}" fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
            <!-- Trolley Frame Arms -->
            <path d="M {tx + (tw * 0.25):.1f} {bottom_flange_y:.1f} L {tx + (tw * 0.15):.1f} {ty:.1f} L {tx + (tw * 0.85):.1f} {ty:.1f} L {tx + (tw * 0.75):.1f} {bottom_flange_y:.1f} Z" 
                  fill="#334155" stroke="#0f172a" stroke-width="1.5" />
            <!-- Hoist Machinery Body (Motor + Drum enclosure) -->
            <rect x="{tx:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="{th:.1f}" fill="#0284c7" stroke="#0f172a" stroke-width="2" rx="4" />
            <!-- Motor Housing Details -->
            <rect x="{tx + 8:.1f}" y="{ty + 6:.1f}" width="{tw * 0.45:.1f}" height="{th - 12:.1f}" fill="#0369a1" stroke="#082f49" stroke-width="1" rx="2" />
            <!-- Rope Drum Housing -->
            <rect x="{tx + (tw * 0.52):.1f}" y="{ty + 6:.1f}" width="{tw * 0.42:.1f}" height="{th - 12:.1f}" fill="#075985" stroke="#082f49" stroke-width="1" rx="2" />
            <!-- Hoist Identification Label -->
            <text x="{tx + (tw / 2.0):.1f}" y="{ty + (th / 2.0) + 4:.1f}" font-family="Arial, sans-serif" font-size="{max(9.0, min(14.0, th * 0.24)):.1f}" 
                  font-weight="bold" fill="#ffffff" text-anchor="middle">HOIST UNIT</text>
        </g>
        """

    def _render_hook_block(self) -> str:
        lo = self.layout
        hw = lo.hook_block_width_px
        hh = lo.hook_block_height_px
        cx = lo.trolley_center_x
        top_y = lo.hook_top_y
        hx = cx - (hw / 2.0)

        # Wire rope falls from trolley drum to hook sheave
        rope_spacing = hw * 0.4
        trolley_drum_y = lo.trolley_top_y + lo.trolley_height_px

        return f"""
        <!-- Hoist Wire Ropes & Hook Block -->
        <g id="hook-block">
            <!-- Wire Rope Falls -->
            <line x1="{cx - rope_spacing:.1f}" y1="{trolley_drum_y:.1f}" x2="{cx - rope_spacing:.1f}" y2="{top_y:.1f}" stroke="#334155" stroke-width="2" />
            <line x1="{cx + rope_spacing:.1f}" y1="{trolley_drum_y:.1f}" x2="{cx + rope_spacing:.1f}" y2="{top_y:.1f}" stroke="#334155" stroke-width="2" />
            
            <!-- Sheave Block Casing -->
            <rect x="{hx:.1f}" y="{top_y:.1f}" width="{hw:.1f}" height="{hh * 0.55:.1f}" fill="#eab308" stroke="#0f172a" stroke-width="2" rx="4" />
            <!-- Sheave Pins -->
            <circle cx="{cx - (hw * 0.22):.1f}" cy="{top_y + (hh * 0.28):.1f}" r="{hw * 0.16:.1f}" fill="#ca8a04" stroke="#713f12" stroke-width="1" />
            <circle cx="{cx + (hw * 0.22):.1f}" cy="{top_y + (hh * 0.28):.1f}" r="{hw * 0.16:.1f}" fill="#ca8a04" stroke="#713f12" stroke-width="1" />
            <circle cx="{cx - (hw * 0.22):.1f}" cy="{top_y + (hh * 0.28):.1f}" r="3" fill="#ffffff" />
            <circle cx="{cx + (hw * 0.22):.1f}" cy="{top_y + (hh * 0.28):.1f}" r="3" fill="#ffffff" />
            
            <!-- Swivel Neck & Forged Hook -->
            <rect x="{cx - 5:.1f}" y="{top_y + (hh * 0.55):.1f}" width="10" height="{hh * 0.12:.1f}" fill="#1e293b" />
            <!-- Hook Profile Body -->
            <path d="M {cx:.1f} {top_y + (hh * 0.65):.1f} 
                     C {cx + (hw * 0.35):.1f} {top_y + (hh * 0.70):.1f}, {cx + (hw * 0.45):.1f} {top_y + (hh * 0.95):.1f}, {cx:.1f} {top_y + hh:.1f} 
                     C {cx - (hw * 0.45):.1f} {top_y + hh:.1f}, {cx - (hw * 0.45):.1f} {top_y + (hh * 0.75):.1f}, {cx - (hw * 0.1):.1f} {top_y + (hh * 0.78):.1f} 
                     C {cx - (hw * 0.25):.1f} {top_y + (hh * 0.85):.1f}, {cx - (hw * 0.15):.1f} {top_y + (hh * 0.92):.1f}, {cx:.1f} {top_y + (hh * 0.92):.1f}
                     C {cx + (hw * 0.2):.1f} {top_y + (hh * 0.92):.1f}, {cx + (hw * 0.15):.1f} {top_y + (hh * 0.78):.1f}, {cx:.1f} {top_y + (hh * 0.72):.1f} Z" 
                  fill="#1e293b" stroke="#0f172a" stroke-width="1.5" />
            <!-- Safety Latch -->
            <line x1="{cx:.1f}" y1="{top_y + (hh * 0.72):.1f}" x2="{cx - (hw * 0.12):.1f}" y2="{top_y + (hh * 0.82):.1f}" stroke="#dc2626" stroke-width="2" />
        </g>
        """

    def _render_reference_lines(self) -> str:
        lo = self.layout
        svg = [
            f"""
        <!-- Engineering Datum & Reference Lines -->
        <g id="reference-lines" stroke="#94a3b8" stroke-width="1" stroke-dasharray="8,4">
            <!-- Centerline of Span -->
            <line x1="{lo.canvas_width / 2.0:.1f}" y1="80" x2="{lo.canvas_width / 2.0:.1f}" y2="{lo.lowest_hook_y + 60:.1f}" />
            <text x="{lo.canvas_width / 2.0:.1f}" y="70" font-family="Arial, sans-serif" font-size="11" fill="#64748b" text-anchor="middle">CL CRANE SPAN</text>
            
            <!-- Top of Rail Reference Level -->
            <line x1="60" y1="{lo.rail_top_y:.1f}" x2="{lo.canvas_width - 60:.1f}" y2="{lo.rail_top_y:.1f}" />
            <text x="65" y="{lo.rail_top_y - 6:.1f}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#475569">RL (RAIL LEVEL)</text>
            
            <!-- Lowest Hook Travel Level / Lifting Datum -->
            <line x1="{lo.trolley_center_x - (lo.span_px * 0.4):.1f}" y1="{lo.lowest_hook_y:.1f}" 
                  x2="{lo.trolley_center_x + (lo.span_px * 0.4):.1f}" y2="{lo.lowest_hook_y:.1f}" />
            <text x="{lo.trolley_center_x - (lo.span_px * 0.4):.1f}" y="{lo.lowest_hook_y - 6:.1f}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#475569">LOWEST HOOK POSITION</text>
        </g>
        """
        ]
        return "".join(svg)

    def _render_dimension_annotations(self) -> str:
        """
        Renders clear, non-overlapping engineering dimension lines with extension lines,
        arrows, and exact numerical annotations for all 8 parameters.
        """
        lo = self.layout
        svg = ['<!-- Dimension Annotations -->', '<g id="dimension-lines">']

        # 1. Overall Crane Span Dimension (Top horizontal dimension line)
        span_dim_y = lo.girder_top_y - 45.0
        svg.append(self._draw_horizontal_dimension(
            x1=lo.left_rail_center_x,
            x2=lo.right_rail_center_x,
            y=span_dim_y,
            ext_y_start=lo.rail_top_y,
            text=f"SPAN: {lo.span_mm:,.0f} mm",
            placement="above"
        ))

        # 2. Main Girder Depth (Vertical dimension on left)
        g_dim_x = lo.girder_left_x + 55.0
        svg.append(self._draw_vertical_dimension(
            y1=lo.girder_top_y,
            y2=lo.girder_bottom_y,
            x=g_dim_x,
            ext_x_start=lo.girder_left_x,
            text=f"GIRDER DEPTH: {lo.girder_depth_mm:,.0f} mm",
            placement="right"
        ))

        # 3. End Carriage Height (Vertical dimension on Right End Carriage)
        rc_dim_x = lo.right_rail_center_x + (lo.end_carriage_width_px / 2.0) + 35.0
        rc_top_y = lo.rail_top_y - lo.end_carriage_height_px + (lo.runway_rail_height_px * 0.9)
        svg.append(self._draw_vertical_dimension(
            y1=rc_top_y,
            y2=rc_top_y + lo.end_carriage_height_px,
            x=rc_dim_x,
            ext_x_start=lo.right_rail_center_x + (lo.end_carriage_width_px / 2.0),
            text=f"END CARRIAGE HEIGHT: {lo.end_carriage_height_mm:,.0f} mm",
            placement="right"
        ))

        # 4. Runway Rail Height (Vertical dimension on Left Rail)
        rail_dim_x = lo.left_rail_center_x - (lo.runway_rail_width_px / 2.0) - 30.0
        svg.append(self._draw_vertical_dimension(
            y1=lo.rail_top_y,
            y2=lo.rail_top_y + lo.runway_rail_height_px,
            x=rail_dim_x,
            ext_x_start=lo.left_rail_center_x - (lo.runway_rail_width_px / 2.0),
            text=f"RAIL HT: {lo.runway_rail_height_mm:,.0f} mm",
            placement="left"
        ))

        # 5. Hoist/Trolley Width (Horizontal dimension directly above trolley)
        tw_y = lo.trolley_top_y - 12.0
        tx1 = lo.trolley_center_x - (lo.trolley_width_px / 2.0)
        tx2 = lo.trolley_center_x + (lo.trolley_width_px / 2.0)
        svg.append(self._draw_horizontal_dimension(
            x1=tx1,
            x2=tx2,
            y=tw_y,
            ext_y_start=lo.trolley_top_y + 10.0,
            text=f"TROLLEY WIDTH: {lo.trolley_width_mm:,.0f} mm",
            placement="above"
        ))

        # 6. Hook Block Height (Vertical dimension beside hook block)
        hook_dim_x = lo.trolley_center_x + (lo.hook_block_width_px / 2.0) + 25.0
        svg.append(self._draw_vertical_dimension(
            y1=lo.hook_top_y,
            y2=lo.hook_bottom_y,
            x=hook_dim_x,
            ext_x_start=lo.trolley_center_x + (lo.hook_block_width_px / 2.0),
            text=f"HOOK BLOCK HT: {lo.hook_block_height_mm:,.0f} mm",
            placement="right"
        ))

        # 7. Lifting Height (Vertical dimension from rail level down to lowest hook position)
        lift_dim_x = lo.trolley_center_x - (lo.span_px * 0.28)
        svg.append(self._draw_vertical_dimension(
            y1=lo.rail_top_y,
            y2=lo.lowest_hook_y,
            x=lift_dim_x,
            ext_x_start=lo.left_rail_center_x + 50.0,
            text=f"LIFTING HEIGHT: {lo.lifting_height_mm:,.0f} mm",
            placement="left"
        ))

        svg.append('</g>')
        return "\n".join(svg)

    def _draw_horizontal_dimension(self, x1: float, x2: float, y: float, ext_y_start: float, text: str, placement: str = "above") -> str:
        text_y = y - 7.0 if placement == "above" else y + 16.0
        ext_overshoot = 8.0
        return f"""
        <!-- Horizontal Dimension: {text} -->
        <g class="dim-annotation">
            <line x1="{x1:.1f}" y1="{ext_y_start:.1f}" x2="{x1:.1f}" y2="{y - ext_overshoot if placement == 'above' else y + ext_overshoot:.1f}" stroke="#64748b" stroke-width="0.8" />
            <line x1="{x2:.1f}" y1="{ext_y_start:.1f}" x2="{x2:.1f}" y2="{y - ext_overshoot if placement == 'above' else y + ext_overshoot:.1f}" stroke="#64748b" stroke-width="0.8" />
            <line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="#0f172a" stroke-width="1.2" 
                  marker-start="url(#arrow-start)" marker-end="url(#arrow-end)" />
            <rect x="{(x1 + x2) / 2.0 - 75:.1f}" y="{text_y - 11:.1f}" width="150" height="15" fill="#ffffff" opacity="0.9" rx="2" />
            <text x="{(x1 + x2) / 2.0:.1f}" y="{text_y:.1f}" font-family="Consolas, Monaco, monospace" font-size="11" font-weight="bold" 
                  fill="#0f172a" text-anchor="middle">{text}</text>
        </g>
        """

    def _draw_vertical_dimension(self, y1: float, y2: float, x: float, ext_x_start: float, text: str, placement: str = "right") -> str:
        text_x = x + 8.0 if placement == "right" else x - 8.0
        anchor = "start" if placement == "right" else "end"
        ext_overshoot = 8.0
        return f"""
        <!-- Vertical Dimension: {text} -->
        <g class="dim-annotation">
            <line x1="{ext_x_start:.1f}" y1="{y1:.1f}" x2="{x + ext_overshoot if placement == 'right' else x - ext_overshoot:.1f}" y2="{y1:.1f}" stroke="#64748b" stroke-width="0.8" />
            <line x1="{ext_x_start:.1f}" y1="{y2:.1f}" x2="{x + ext_overshoot if placement == 'right' else x - ext_overshoot:.1f}" y2="{y2:.1f}" stroke="#64748b" stroke-width="0.8" />
            <line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="#0f172a" stroke-width="1.2" 
                  marker-start="url(#arrow-start)" marker-end="url(#arrow-end)" />
            <text x="{text_x:.1f}" y="{(y1 + y2) / 2.0 + 4:.1f}" font-family="Consolas, Monaco, monospace" font-size="10" font-weight="bold" 
                  fill="#0f172a" text-anchor="{anchor}">{text}</text>
        </g>
        """

    def _render_title_block(self) -> str:
        lo = self.layout
        tb_w = 460.0
        tb_h = 140.0
        tb_x = lo.canvas_width - tb_w - 30.0
        tb_y = lo.canvas_height - tb_h - 30.0

        today_str = datetime.now().strftime("%Y-%m-%d")

        return f"""
        <!-- Professional Engineering Title Block -->
        <g id="title-block">
            <rect x="{tb_x:.1f}" y="{tb_y:.1f}" width="{tb_w:.1f}" height="{tb_h:.1f}" fill="#ffffff" stroke="#0f172a" stroke-width="1.8" />
            <line x1="{tb_x:.1f}" y1="{tb_y + 35:.1f}" x2="{tb_x + tb_w:.1f}" y2="{tb_y + 35:.1f}" stroke="#0f172a" stroke-width="1.2" />
            <line x1="{tb_x:.1f}" y1="{tb_y + 70:.1f}" x2="{tb_x + tb_w:.1f}" y2="{tb_y + 70:.1f}" stroke="#0f172a" stroke-width="1.2" />
            <line x1="{tb_x:.1f}" y1="{tb_y + 105:.1f}" x2="{tb_x + tb_w:.1f}" y2="{tb_y + 105:.1f}" stroke="#0f172a" stroke-width="1.2" />
            <line x1="{tb_x + 280:.1f}" y1="{tb_y + 35:.1f}" x2="{tb_x + 280:.1f}" y2="{tb_y + 105:.1f}" stroke="#0f172a" stroke-width="1.2" />

            <!-- Title & Project -->
            <text x="{tb_x + 12:.1f}" y="{tb_y + 22:.1f}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#0f172a">PARAMETRIC OVERHEAD CRANE GENERATOR</text>
            <text x="{tb_x + 360:.1f}" y="{tb_y + 22:.1f}" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0284c7">REV: 01 (V1)</text>

            <!-- Drawing Subject -->
            <text x="{tb_x + 12:.1f}" y="{tb_y + 52:.1f}" font-family="Arial, sans-serif" font-size="9" fill="#64748b">DRAWING TITLE / TYPE</text>
            <text x="{tb_x + 12:.1f}" y="{tb_y + 65:.1f}" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0f172a">FRONT ELEVATION — SINGLE-GIRDER CRANE</text>

            <!-- SWL / Capacity -->
            <text x="{tb_x + 290:.1f}" y="{tb_y + 52:.1f}" font-family="Arial, sans-serif" font-size="9" fill="#64748b">SAFE WORKING LOAD</text>
            <text x="{tb_x + 290:.1f}" y="{tb_y + 65:.1f}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#0284c7">{lo.capacity_t:g} TONNES</text>

            <!-- Design Reference -->
            <text x="{tb_x + 12:.1f}" y="{tb_y + 87:.1f}" font-family="Arial, sans-serif" font-size="9" fill="#64748b">DESIGN REFERENCE</text>
            <text x="{tb_x + 12:.1f}" y="{tb_y + 100:.1f}" font-family="Arial, sans-serif" font-size="11" font-weight="bold" fill="#0f172a">{self.design_name}</text>

            <!-- Date & Units -->
            <text x="{tb_x + 290:.1f}" y="{tb_y + 87:.1f}" font-family="Arial, sans-serif" font-size="9" fill="#64748b">DATE / UNITS</text>
            <text x="{tb_x + 290:.1f}" y="{tb_y + 100:.1f}" font-family="Arial, sans-serif" font-size="10" font-weight="bold" fill="#0f172a">{today_str} | mm</text>

            <!-- Disclaimer Notice -->
            <text x="{tb_x + 12:.1f}" y="{tb_y + 125:.1f}" font-family="Arial, sans-serif" font-size="8.5" font-weight="bold" fill="#dc2626">
                PROTOTYPE DRAWING — NOT A CERTIFIED CRANE ENGINEERING DESIGN
            </text>
        </g>
        """


def generate_crane_svg(params: Dict[str, Any], design_name: str = "Parametric Crane Design") -> str:
    """
    Convenience function to generate SVG markup from parameters.
    """
    generator = CraneDrawingGenerator(params, design_name=design_name)
    return generator.generate_svg()
