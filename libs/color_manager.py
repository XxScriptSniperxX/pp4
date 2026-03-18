# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 11:44:01 2026

@tag: Xx_ScriptSniper_xX

@author: Albin
"""
import itertools

# Accessible color palettes (expandable pool)
PALETTE_POOL = {
    "Okabe-Ito (Color Universal Design)": [
        "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7"
    ],
    "ColorBrewer Set2": [
        "#66c2a5", "#fc8d62", "#8da0cb",
        "#e78ac3", "#a6d854", "#ffd92f",
        "#e5c494", "#b3b3b3"
    ],
    "Grayscale": [
        "#000000", "#555555", "#AAAAAA", "#DDDDDD"
    ]
}

class ColorManager:
    def __init__(self, ui_colors=None, plot_colors=None, max_axes=5, max_perps=10):
        ui_colors = ui_colors or {}
        plot_colors = plot_colors or {}

        # --- App theme ---
        self.primary = ui_colors.get("primary", "#0072B2")
        self.text = ui_colors.get("text", "#000000")
        self.background = ui_colors.get("background", "#FFFFFF")
        self.secondary = ui_colors.get("secondary", "#DDDDDD")

        # --- Plot theme (global defaults) ---
        self.axis_title_color = plot_colors.get("axis_title", "#000000")
        self.tick_label_color = plot_colors.get("tick_label", "#000000")
        self.legend_text_color = plot_colors.get("legend_text", "#000000")
        self.plot_title_color = plot_colors.get("plot_title", "#000000")
        self.plot_bgcolor = plot_colors.get("plot_bg", "#FFFFFF")
        self.grid_color = plot_colors.get("grid", "#DDDDDD")

        # Palette pool (secondary priority)
        palette_name = plot_colors.get("palette_name", "Okabe-Ito (Color Universal Design)")
        self.palette = PALETTE_POOL.get(palette_name, PALETTE_POOL["Okabe-Ito (Color Universal Design)"])
        self.use_palette = plot_colors.get("use_palette", False)

        # --- Explicit 16 line colors (primary priority) ---
        self.line_palette = []
        for i in range(16):
            key = f"plot_line_color{i+1}"
            self.line_palette.append(plot_colors.get(key, None))

    def _shade_color(self, hex_color, factor=0.8):
        hex_color = hex_color.lstrip("#")
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def get_trace_color(self, index):
        """Priority: explicit 16 palette → palette pool → default blue."""
        # 1. Explicit 16-color palette
        if index < len(self.line_palette) and self.line_palette[index]:
            return self.line_palette[index]

        # 2. Palette pool cycling/shading
        if self.use_palette and self.palette:
            palette_len = len(self.palette)
            base_color = self.palette[index % palette_len]
            factor = 0.7 + 0.1 * (index // palette_len)
            return self._shade_color(base_color, factor)

        # 3. Fallback default
        return "#0072B2"

    def get_style(self, key, is_primary=False):
        color = self.get_trace_color(key)
        return {"color": color, "dash": "dash", "marker": "circle"}

    def apply_to_fig(self, fig, x_title="X", y_title="Y", plot_title="Plot"):
        fig.update_layout(
            title=dict(text=plot_title, font=dict(color=self.plot_title_color)),
            legend=dict(font=dict(color=self.legend_text_color)),
            xaxis=dict(
                title=x_title,
                titlefont=dict(color=self.axis_title_color),
                tickfont=dict(color=self.tick_label_color),
                gridcolor=self.grid_color
            ),
            yaxis=dict(
                title=y_title,
                titlefont=dict(color=self.axis_title_color),
                tickfont=dict(color=self.tick_label_color),
                gridcolor=self.grid_color
            ),
            plot_bgcolor=self.plot_bgcolor,
            paper_bgcolor=self.plot_bgcolor
        )
        return fig
